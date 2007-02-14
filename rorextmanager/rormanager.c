#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include <curl/curl.h>
#include <curl/types.h>
#include <curl/easy.h>

#include <libxml/xmlmemory.h>
#include <libxml/parser.h>

char *repourl = "https://repository.rigsofrods.com/getexinfo.php?id=";

int getinfo(char *idstr);
int parseDoc(char *docname);
void parseExtInfo (xmlDocPtr doc, xmlNodePtr cur);

struct rorextension {
  char *id;
  char *author;
  char *description;
  size_t filesize;
  size_t depcount;
  char *dependencies[200];
};

struct rorextension ext[50];
size_t extcounter = 0;

size_t write_data(void *ptr, size_t size, size_t nmemb, void *stream)
{
  int written = fwrite(ptr, size, nmemb, (FILE *)stream);
  return written;
}

void parseExtDepInfo (xmlDocPtr doc, xmlNodePtr cur, struct rorextension *r)
{
  r->depcount = 0;
  xmlChar *val;
  cur = cur->xmlChildrenNode;
  while (cur != NULL) {
    val = xmlNodeListGetString(doc, cur->xmlChildrenNode, 1);
    if ((!xmlStrcmp(cur->name, (const xmlChar *)"dependson"))) {
      char *tstr = (char*)malloc(strlen((char *)val));
      strncpy(tstr, (char *)val, strlen((char *)val));
      r->dependencies[r->depcount] = tstr;
      r->depcount++;
    }
    xmlFree(val);
    cur = cur->next;
  }
  return;
}

void parseExtInfo (xmlDocPtr doc, xmlNodePtr cur)
{
  xmlChar *val;
  cur = cur->xmlChildrenNode;
  struct rorextension r;
  int i = 0;

  while (cur != NULL) {
    val = xmlNodeListGetString(doc, cur->xmlChildrenNode, 1);
    if ((!xmlStrcmp(cur->name, (const xmlChar *)"id"))) {
      r.id = (char*)malloc(strlen((char *)val));
      strncpy(r.id, (char *)val, strlen((char *)val));
    } else if ((!xmlStrcmp(cur->name, (const xmlChar *)"author"))) {
      r.author = (char*)malloc(strlen((char *)val));
      strncpy(r.author, (char *)val, strlen((char *)val));
    } else if ((!xmlStrcmp(cur->name, (const xmlChar *)"description"))) {
      r.description = (char*)malloc(strlen((char *)val));
      strncpy(r.description, (char *)val, strlen((char *)val));
    } else if ((!xmlStrcmp(cur->name, (const xmlChar *)"filesize"))) {
      char *tmp = (char*)malloc(strlen((char *)val));
      strncpy(tmp, (char *)val, strlen((char *)val));

      r.filesize = (size_t)strtol(tmp, NULL, 10);
    } else if ((!xmlStrcmp(cur->name, (const xmlChar *)"dependencies"))) {
      parseExtDepInfo(doc, cur, &r);
    }
    xmlFree(val);
    cur = cur->next;
  }
  printf("== extension %s ==\n", r.id);
  printf("author: %s\n", r.author);
  printf("description: %s\n", r.description);
  printf("filesize: %d\n", r.filesize);
  printf("dependencies-count: %d\n", r.depcount);
  if (r.depcount>0) {
    for (i=0;i<r.depcount;i++) {
      printf(" depends on: %s\n", r.dependencies[i]);
      getinfo(r.dependencies[i]);
    }
  }
  ext[extcounter++] = r;
  return;
}

int parseDoc(char *docname)
{
  xmlDocPtr doc;
  xmlNodePtr cur;

  doc = xmlParseFile(docname);

  if (doc == NULL ) {
    fprintf(stderr,"Document not parsed successfully. \n");
    return -1;
  }

  cur = xmlDocGetRootElement(doc);

  if (cur == NULL) {
    fprintf(stderr,"empty document\n");
    xmlFreeDoc(doc);
    return -1;
  }

  if (xmlStrcmp(cur->name, (const xmlChar *) "rorextension")) {
    fprintf(stderr,"document of the wrong type, root node != rorextension");
    xmlFreeDoc(doc);
    return -1;
  }

  parseExtInfo (doc, cur);

  xmlFreeDoc(doc);
  return 0;
}


int getinfo(char *idstr)
{
  CURL *curl;
  CURLcode res;
  FILE *outfile;
  char *tmpfile = "tempout.xml";
  char *url = (char*)malloc(255);
  strncpy(url, repourl, strlen(repourl));
  strncat(url, idstr, strlen(idstr));

  printf(" trying to resolve dependency %s\n", idstr);
  printf(">>%s\n", url);
  curl = curl_easy_init();
  if(curl) {
    curl_easy_setopt(curl, CURLOPT_URL, url);

    curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0);
    curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 0);
    //curl_easy_setopt(curl, CURLOPT_CAPATH, "");
    //curl_easy_setopt(curl, CURLOPT_CAINFO, "cacert.crt");

    curl_easy_setopt(curl, CURLOPT_NOPROGRESS, 1);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_data);
    outfile = fopen(tmpfile,"w");
    if (outfile == NULL) {
      curl_easy_cleanup(curl);
      return -1;
    }
    curl_easy_setopt(curl, CURLOPT_WRITEDATA , outfile);
    res = curl_easy_perform(curl);

    /* always cleanup */
    curl_easy_cleanup(curl);

    fclose(outfile);

    parseDoc(tmpfile);
  }
  return 0;
}

int main(int argc, char *argv[])
{
  if(argc != 2) {
    printf("usage: %s <extensionid 1234-1234-1234-1234-5678>\n", argv[0]);
    return -1;
  }

  getinfo(argv[1]);
  return 0;
}





