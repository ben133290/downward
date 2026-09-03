#ifndef TASK_UTILS_REGISTRY_VARIABLES_H
#define TASK_UTILS_REGISTRY_VARIABLES_H

#include <cstddef>
#include <vector>

class AbstractTask;
class ConditionsProxy;
class VariableProxy;

namespace registry_variables {

class RegistryVariablesProxy {
    const AbstractTask *task;

    void mark_variables(
        const ConditionsProxy &conditions, std::vector<bool> &marked);

public:
    using ItemType = VariableProxy;

    std::vector<std::size_t> registry_variable_ids;

    explicit RegistryVariablesProxy(const AbstractTask &task);
    ~RegistryVariablesProxy() = default;

    std::size_t size() const;

    VariableProxy operator[](std::size_t index) const;

    std::size_t convert_index(std::size_t index) const;
};

extern const RegistryVariablesProxy &get_registry_variables(
    const AbstractTask *task);

}

#endif
