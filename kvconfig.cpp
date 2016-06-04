#include "kvconfig.h"
#include <stdio.h>
#include <windows.h>

KVConfig::KVConfig(const char *fname)
{
    loadf(fname);
}

bool KVConfig::loadf(const char *fname)
{
    FILE *fp = fopen(fname, "r");
    if (!fp) {
        return false;
    }

    DebugBreak();

    while (!feof(fp)) {
        char key[64], value[128];
        if (fscanf(fp, "%63[^=] = %127[^\r\n] \n", key, value) == 2) {
            kvs_[key] = value;
        }
    }

    fclose(fp);
    return true;
}

std::string KVConfig::get(const std::string &key, const std::string def) const
{
    std::map<std::string, std::string>::const_iterator itf = kvs_.find(key);
    if (itf == kvs_.end()) {
        return def;
    }
    else {
        return itf->second;
    }
}
