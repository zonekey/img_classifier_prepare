#ifndef KVCONFIG_H
#define KVCONFIG_H

#include <map>
#include <string>

class KVConfig
{
    std::map<std::string, std::string> kvs_;

public:
    explicit KVConfig(const char *fname);

    std::string get(const std::string &key, const std::string def = "") const;

private:
    bool loadf(const char *fname);
};

#endif // KVCONFIG_H
