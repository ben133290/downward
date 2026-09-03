#include "registry_variables.h"

#include "../task_proxy.h"

#include <cassert>
#include <unordered_map>

using namespace std;

namespace registry_variables {

static unordered_map<const AbstractTask *, unique_ptr<RegistryVariablesProxy>>
    registry_variables_cache;

const RegistryVariablesProxy &get_registry_variables(const AbstractTask *task) {
    if (registry_variables_cache.count(task) == 0) {
        registry_variables_cache.insert(
            make_pair(task, make_unique<RegistryVariablesProxy>(*task)));
    }
    return *registry_variables_cache[task];
}

void RegistryVariablesProxy::mark_variables(
    const ConditionsProxy &conditions, std::vector<bool> &marked) {
    for (FactProxy fact : conditions) {
        int var_id = fact.get_variable().get_id();

        if (!marked[var_id]) {
            marked[var_id] = true;
            registry_variable_ids.push_back(var_id);
        }
    }
}

RegistryVariablesProxy::RegistryVariablesProxy(const AbstractTask &task)
    : task(&task) {
    std::vector<bool> marked(task.get_num_variables(), false);

    // primary variables
    for (int id = 0; id < task.get_num_variables(); id++) {
        VariableProxy var(task, id);

        if (!var.is_derived()) {
            marked[id] = true;
            registry_variable_ids.push_back(id);
        }
    }

    // precondition derived
    for (OperatorProxy op : OperatorsProxy(task)) {
        mark_variables(op.get_preconditions(), marked);

        for (EffectProxy effect : op.get_effects()) {
            mark_variables(effect.get_conditions(), marked);
        }
    }

    mark_variables(GoalsProxy(task), marked);
}

std::size_t RegistryVariablesProxy::size() const {
    return registry_variable_ids.size();
}

VariableProxy RegistryVariablesProxy::operator[](std::size_t index) const {
    assert(index < size());
    return VariableProxy(*task, registry_variable_ids[index]);
}

std::size_t RegistryVariablesProxy::convert_index(std::size_t index) const {
    std::size_t registry_index;
    bool found_index = false;
    for (std::size_t i = 0; i < size(); ++i) {
        if (registry_variable_ids[i] == index) {
            registry_index = i;
            found_index = true;
            break;
        }
    }
    if (!found_index) {
        utils::exit_with(utils::ExitCode::SEARCH_CRITICAL_ERROR);
    }
    return registry_index;
}

}
