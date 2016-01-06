#Lepes:
# Be aware with \n characters !! duplitate to \\n in constants and \t too :(

cache = "cache_file = getSetting('Cache Path') .. '%s.dat'"
fileend = "log('%s file loaded successfully')"

basicText = """
-- thanks to sweetman for contributing parts of the race store code
races = {}
diff = {}
racescount = 0
penalties = 0
level = 1
currentrace = ''
trackpenalty = false


function writeScore()
    -- save all content deleting the first one
    local f = io.open(cache_file, 'w')
    if f == nil then
        log('race score file could not be opened to write scores')
    else
        f:write(level)
        for i,r in ipairs(races) do
            f:write('\\n'..r[1]..'|'..races[r[1]]['besttime'])
        end
        f:close()
        log('race score file written')
    end
end

function formatPartialTime(sec)
	-- return a string:
	-- (+3 min 2 sec)
    -- (-34 sec)
    -- <empty string>
    
    local asec = math.abs(sec)
    local m = math.modf (asec / 60)
    local s = math.modf (asec % 60)
    st = string.format('%02.0f',s)..' sec'
    if m > 0 then
        st = string.format('%2.0f', m)..':'..st
    end
    if sec > 0.0 then st = ' (+'..st..')'
    elseif sec < 0.0 then st = ' (-'..st..')'
    else st = ''
    end
    return st
end

function checkPenalty(racename, atchk)
    -- increase penalty time if the race support it
    -- one checkpoint has only one penalty
    if not races[racename]['usepenalization'] then return end
    if table.getn(races[racename]['penalties']) >= atchk then
        if races[racename]['penalties'][atchk] then return    end
    end
    races[racename]['penalties'][atchk] = true
    penalties = races[racename]['penaltytime'] + penalties
    trackpenalty = false
end

function formatSeconds(sec)
	-- return a string:
	-- 3 min 2 sec
    -- 34 sec
    
    local m = math.modf (sec / 60)
    local s = math.modf (sec % 60)
    st = string.format('%02.0f',s)..' sec'
    if m > 0 then
        st = string.format('%2.0f', m)..':'..st
    end
    return st
end

function findScore(racename)
    -- try to read Score for the given racename on disk
    -- return 9999 if fail to load score file
    
    minval = 9999
    local f = io.open(cache_file, 'r')
    if f == nil then return minval end
    for line in f:lines() do
        line_ar = explode('|', line)
        if table.getn(line_ar) > 1 then
            if line_ar[1] == racename and tonumber(line_ar[2]) < minval then
                minval = tonumber(line_ar[2])
            end
        end
    end
    f:close()
    log('race score file read')
    return minval
end

function resetRace()
    -- ability to Stop the current race

    setupArrow(-1)
    -- reset some values
    if currentrace ~= '' then
        races[currentrace]['checkpointspassed'] = 0
        races[currentrace]['penalties'] = {}
		stopTimer()
    end
    currentrace = ''
    penalties = 0
end

function showInfo(hardness)
	-- This function indicates the user which race to run when crossing a large gate (green/orange/red)
	
	diff[0] = 'easy'
	diff[1] = 'medium'
	diff[2] = 'hard'
	maxLevel[0] = 3
	maxLevel[1] = 6
	maxLevel[2] = 9
	racesCompleted = level - 1 - maxLevel[hardness] + 3
	if racesCompleted < 0 then racesCompleted = 0 end
	-- if all races in the level have been completed tell the user to try next level
	if level > maxLevel[hardness] then
		if hardness == 3 then
			msg = diff[hardness]..' level\\nAll races completed, congratulations! Post your times on Rigs on Rods forum!'
		else
			msg = diff[hardness]..' level\\nAll races completed, congratulations! Try '..diff[hardness + 1]..' level.'
		end
	-- if no races of this level have been unlocked tell the user which race to complete
	elseif level < maxLevel[hardness] - 2 then
		msg = diff[hardness]..' level - locked.\\nWin golden medals for all races in '..diff[hardness - 1]..' level to unlock.'
	-- tell the user how many races he completed  in the present difficulty level
	else
		msg = diff[hardness]..' level\\nRaces completed: '..racesCompleted..'/3'
	end
    flashMessage(msg, 4)
end

function cheat()
	flashMessage('aw', 4)
end

function loadCheckpoints(race)
    -- spawn all checkpoints of a race
    
    for a,v in ipairs(races[race]['positions']) do
        if a > 1 then
        -- first checkpoint is already spawn
            iname = 'race_'..race..'_'..a
            log('spawn chk number '..a..' of race '..race..' odef file '..v[7]..' luaName '..iname)
            spawnObject(v[7], iname, v[1],v[2],v[3], v[4],v[5],v[6], raceEventHandler)
        end
    end
end


function setupRace(racename, positions, loop, showaltitude)
	--SetupRace has several parameters:
	--  racename to show on screen (no spaces nor underscore)
	--  array of checkpoints positions
	-- is loop ?
	--  Print Altitude of the next checkpoint on screen ?

    log('setup race '..racename)
    racescount = racescount + 1
    if table.getn(positions) > 1 then
		spawnObject(positions[1][7], 'race_'..racename..'_1', positions[1][1],positions[1][2],positions[1][3], positions[1][4],positions[1][5],positions[1][6], raceEventHandler)
		log('spawned checkpoint number 1 of race '..racename..' odef file '..positions[1][7]..' luaName '..'race_'..racename..'_1' )
    end
    -- add the race finally
    races[racename] = {}
    races[racename]['racename'] = racename
    races[racename]['positions'] = positions
    races[racename]['isloop'] = loop
    races[racename]['startTime'] = 0
    races[racename]['lastcheckpoint'] = 1
    races[racename]['checkpointspassed'] = 1
    races[racename]['numcheckpoints'] = table.getn(positions)
    races[racename]['checkpointsloaded'] = false
    races[racename]['showaltitude'] = showaltitude
    races[racename]['usepenalization'] = false
    races[racename]['penaltytime'] = 0.0
    races[racename]['penalties'] = {}
    races[racename]['goldentime'] = 0.0
    races[racename]['platetime'] = 0.0
    races[racename]['bronzetime'] = 0.0
    races[racename]['idxrace'] = racescount
    races[racename]['besttime'] = findScore(racename)
    if loop then
        races[racename]['goalnum'] = 1
    else
        races[racename]['goalnum'] = table.getn(positions)
    end

end

function nextRace(something)
    -- if races are chainned, with this function you can configure what is the 
    -- next race of the actual one
    
    for a,v in ipairs(races) do
        if races[v[1]]['idxrace'] == something then
            local iname = 'race_'..v[1]..'_1'
            local position = races[v[1]]['positions'][1]
            spawnObject(position[7], iname, position[1],position[2],position[3], position[4],position[5],position[6], raceEventHandler)
            log('spawn chk number 1 of race '..v[1]..' odef file '..position[7]..' luaName '..iname)
			return
        end
    end
end


function getMedal(racename, spent)
    -- return a string with the Medal based on some times predefined. 
    -- You need to setup races[racename]['goldentime'], platetime and bronzetime
    -- before you call this routine
    
    if spent <= races[racename]['goldentime'] then
        return 'Golden'
    elseif spent <= races[racename]['platetime'] then
        return 'Plate'
    elseif spent <= races[racename]['bronzetime'] then
        return 'Bronze'
    else
        return '\\t'
    end
end

function getCheckPointFromName(instance)
    -- checkpoint names are like this: race_Mountain break_3
    -- "race_" is a preffix
    -- where the left part from the undescore character is the racename
    -- and the riht part is the number of the checkpoint (zero based)
    
    ar = explode('_', instance)
    if table.getn(ar) < 3 then return -1
    else
        return tonumber(ar[3])
    end
end

function getRacenameFromName(instance)
    -- get the name of the race from the checkpoint name (instance parameter)
    ar = explode('_', instance)
    if table.getn(ar) < 2 then return ''
    else
        return tostring(ar[2])
    end
end

function setupArrow(position)
    if position == -1 or position == nil then
        -- hide it
        pointArrow(0, 0, 0, '')
    else
        txt = currentrace..'\\ncheckpoint '..tostring(position)..' / '..races[currentrace]['numcheckpoints']
        if position == 1 and races[currentrace]['isloop'] then
            txt = 'Finish'
        end
        data = races[currentrace]['positions'][position]
        if data then
            if races[currentrace]['showaltitude'] then
                txt = txt .. '\\n\\nAlt '..string.format('%.0f', races[currentrace]['positions'][position][2] * 3,2808399 )..' feets'
            end
            pointArrow(data[1], data[2], data[3], txt)
        else
            pointArrow(0, 0, 0, '')
        end
    end
end

function raceEventHandler(instance, box)
    -- Main function to control race logic
    -- every time user cross a checkpoint or an object that has an event defined
    -- this function is automatically executed
    
    -- instance is: race_Mountain Break_<number of checkpoint>
    -- box is the defined event in .odef file, that is, the event name.
    -- You cn create your own event names on odef file, modifying this routine.
    
    checknum = getCheckPointFromName(instance)
    racename = getRacenameFromName(instance)

    if box == 'resetcurrentrace'  then
        resetRace()
    elseif box == 'penalty' then
        trackpenalty = true
		flashMessage('PENALTY!',2)
	elseif box == 'showinfogreen' then
		showInfo(0)
	elseif box == 'showinfoorange' then
		showInfo(1)
	elseif box == 'showinfored' then
		showInfo(2)
	elseif box == 'cheat' then
		showInfo(0)
    else
        -- create an array with all required names in it
        if currentrace == '' then
            -- not racing currently
            if checknum == 1 then
                -- start of the race
                currentrace = racename
                races[currentrace]['startTime'] = getTime()
                races[currentrace]['lastcheckpoint'] = 1
                races[currentrace]['checkpointspassed'] = 1
                if not races[racename]['checkpointsloaded'] then
                    loadCheckpoints(racename)
                    races[racename]['checkpointsloaded'] = true
                end
                if trackpenalty then checkPenalty(racename, checknum) end
                setupArrow(2)
                startTimer()
                msg = racename..' started!'
                flashMessage(msg, 4)
            end
        elseif currentrace == racename then
            -- we hit a checkpoint from the same race!
            if checknum == races[currentrace]['lastcheckpoint'] + 1 then
                -- racing, correct checkpoint!
                if checknum == races[currentrace]['numcheckpoints'] and races[currentrace]['isloop'] then
                    setupArrow(1)
                else
                    setupArrow(checknum+1)
                end
                races[currentrace]['lastcheckpoint'] = checknum
                races[currentrace]['checkpointspassed'] = races[currentrace]['checkpointspassed'] + 1
                if trackpenalty then checkPenalty(racename, checknum) end
                time = getTime() - races[currentrace]['startTime']
                msg = 'Completed: '..checknum..'/'..(races[currentrace]['numcheckpoints'])..' in '..formatSeconds(time)
                flashMessage(msg, 4)
            else
                if not checknum == races[currentrace]['lastcheckpoint'] then
                    -- racing, wrong checkpoint, prevent trigger of the same checkpoint twice
                    flashMessage('Wrong gate! You must find and pass Checkpoint '..races[currentrace]['lastcheckpoint'] + 1, 4)
                end
            end
            if checknum == races[currentrace]['goalnum'] and races[currentrace]['checkpointspassed'] == races[racename]['numcheckpoints'] then
                -- racing, reached finish
                --time = getTime() - starttime
                line1 = ''
                line2 = ''
                time = stopTimer()
                if races[racename]['usepenalization']  then
                    line1 = 'penalty \\t\\t\\t '..line1 --one more tab than line2
                    line2 = formatSeconds(penalties)..'\\t\\t '
                end
                line1 = 'Medal \\t\\ttime\\t\\t'.. line1..'final time'
                line2 = getMedal(racename, time).. '\\t\\t'..formatSeconds(time)..'\\t\\t'..line2..formatSeconds(time + penalties)
                time = time + penalties
                local savescores = false
                if time < races[currentrace]['goldentime'] and level < 9 then
                    level = level + 1
                    nextRace(level)
                    savescores = true
                end
                if time < tonumber(races[currentrace]['besttime']) then
                    line2 = line2 .. '\\nNew Best Lap Time!'
                    if tonumber(races[currentrace]['besttime']) ~= 9999 then
                        line2 = line2.. formatPartialTime(time - races[currentrace]['besttime'])
                    end
                    races[currentrace]['besttime'] = time
                    savescores = true
                    if time < races[currentrace]['goldentime'] and level < 9 then
                        line2 = line2..'\\n Unlocked next race, good work!'
                    end
                else
                    line2 = line2 .. '\\n (Best Lap: '..formatSeconds(races[currentrace]['besttime'])..')'
                end
                if savescores then writeScore() end
                log(currentrace..' finished. Score:\\n'..line1..'\\n'..line2)
                flashMessage(line1..'\\n'..line2, 15)
                resetRace()
            end
        else
            -- flashMessage('This Checkpoint belongs to race'..racename..'!', 4)
        end
    end
end
-- Toolkit scan begin here
"""
