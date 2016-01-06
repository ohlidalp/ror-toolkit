function geshi_toggle_code(id)
{
	if(!$("#"+id).hasClass('geshicodeHidden'))
	{
		$("#"+id).addClass('geshicodeHidden');
		$("#"+id+"_plain").removeClass('geshicodeHidden');
	} else
	{
		$("#"+id).removeClass('geshicodeHidden');
		$("#"+id+"_plain").addClass('geshicodeHidden');
	}
}

function geshi_select_code(id)
{
	if(!$("#"+id).hasClass('geshicodeHidden'))
		geshi_toggle_code(id);
	$("#"+id+"_text").focus().select();
	//$("#"+id+"_btnselect").attr("disabled", "true");
}

function geshi_show_full(id)
{
	if($("#"+id).hasClass('geshicodeHidden'))
		return;

	if($("#"+id).hasClass('geshicodeScroll'))
	{
		$("#"+id).removeClass('geshicodeScroll');
		$("#"+id+"_btnfull").attr("value", "hide full");
	} else
	{
		$("#"+id).addClass('geshicodeScroll');
		$("#"+id+"_btnfull").attr("value", "show full");
	}
}
