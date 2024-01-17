"""本模块为 NoneBot 插件开发提供便携的定义函数。

## 快捷导入

为方便使用，本模块从子模块导入了部分内容，以下内容可以直接通过本模块导入:

- `on` => {ref}``on` <nonebot.plugin.on.on>`
- `on_metaevent` => {ref}``on_metaevent` <nonebot.plugin.on.on_metaevent>`
- `on_message` => {ref}``on_message` <nonebot.plugin.on.on_message>`
- `on_notice` => {ref}``on_notice` <nonebot.plugin.on.on_notice>`
- `on_request` => {ref}``on_request` <nonebot.plugin.on.on_request>`
- `on_startswith` => {ref}``on_startswith` <nonebot.plugin.on.on_startswith>`
- `on_endswith` => {ref}``on_endswith` <nonebot.plugin.on.on_endswith>`
- `on_fullmatch` => {ref}``on_fullmatch` <nonebot.plugin.on.on_fullmatch>`
- `on_keyword` => {ref}``on_keyword` <nonebot.plugin.on.on_keyword>`
- `on_command` => {ref}``on_command` <nonebot.plugin.on.on_command>`
- `on_shell_command` => {ref}``on_shell_command` <nonebot.plugin.on.on_shell_command>`
- `on_regex` => {ref}``on_regex` <nonebot.plugin.on.on_regex>`
- `on_type` => {ref}``on_type` <nonebot.plugin.on.on_type>`
- `CommandGroup` => {ref}``CommandGroup` <nonebot.plugin.on.CommandGroup>`
- `Matchergroup` => {ref}``MatcherGroup` <nonebot.plugin.on.MatcherGroup>`
- `load_plugin` => {ref}``load_plugin` <nonebot.plugin.load.load_plugin>`
- `load_plugins` => {ref}``load_plugins` <nonebot.plugin.load.load_plugins>`
- `load_all_plugins` => {ref}``load_all_plugins` <nonebot.plugin.load.load_all_plugins>`
- `load_from_json` => {ref}``load_from_json` <nonebot.plugin.load.load_from_json>`
- `load_from_toml` => {ref}``load_from_toml` <nonebot.plugin.load.load_from_toml>`
- `load_builtin_plugin` =>
  {ref}``load_builtin_plugin` <nonebot.plugin.load.load_builtin_plugin>`
- `load_builtin_plugins` =>
  {ref}``load_builtin_plugins` <nonebot.plugin.load.load_builtin_plugins>`
- `require` => {ref}``require` <nonebot.plugin.load.require>`
- `PluginMetadata` => {ref}``PluginMetadata` <nonebot.plugin.model.PluginMetadata>`

FrontMatter:
    sidebar_position: 0
    description: nonebot.plugin 模块
"""

from itertools import chain
from types import ModuleType
from contextvars import ContextVar
from typing import Set, Dict, List, Tuple, Union, Optional

_plugins: Dict[Union[str, Tuple[str, ...]], "Plugin"] = {}
_managers: List["PluginManager"] = []
_current_plugin_chain: ContextVar[Tuple["Plugin", ...]] = ContextVar(
    "_current_plugin_chain", default=()
)


def _module_name_to_plugin_name(module_name: str) -> str:
    return module_name.rsplit(".", 1)[-1]


def _plugin_name_to_plugin_fullpath(
    plugin_name: str, manager: Optional["PluginManager"] = None
) -> Tuple[str, ...]:
    parents = _current_plugin_chain.get()
    if manager is None:
        return (*(parent.name for parent in parents), plugin_name)
    for pre_plugin in reversed(parents):
        if _managers.index(pre_plugin.manager) < _managers.index(manager):
            return (*pre_plugin.plugin_fullpath, plugin_name)
    else:
        return (plugin_name,)


def _new_plugin(
    module_name: str, module: ModuleType, manager: "PluginManager"
) -> "Plugin":
    plugin_name = _module_name_to_plugin_name(module_name)
    plugin_fullpath = _plugin_name_to_plugin_fullpath(plugin_name, manager)
    if plugin_fullpath in _plugins:
        raise RuntimeError("Plugin already exists! Check your plugin name.")
    plugin = Plugin(plugin_name, module, module_name, manager)
    _plugins[plugin_name] = plugin
    _plugins[plugin_fullpath] = plugin
    return plugin


def _revert_plugin(plugin: "Plugin") -> None:
    if plugin.name not in _plugins:
        raise RuntimeError("Plugin not found!")
    del _plugins[plugin.name]
    del _plugins[plugin.plugin_fullpath]
    if parent_plugin := plugin.parent_plugin:
        parent_plugin.sub_plugins.remove(plugin)


def get_plugin(name: Union[str, Tuple[str, ...]]) -> Optional["Plugin"]:
    """获取已经导入的某个插件。

    如果为 `load_plugins` 文件夹导入的插件，则为文件(夹)名。

    参数:
        name: 插件名或插件路径，即 {ref}`nonebot.plugin.model.Plugin.name`
            或 {ref}`nonebot.plugin.model.Plugin.plugin_fullpath`。
    """
    return _plugins.get(name)


def get_plugin_by_module_name(module_name: str) -> Optional["Plugin"]:
    """通过模块名获取已经导入的某个插件。

    如果提供的模块名为某个插件的子模块，同样会返回该插件。

    参数:
        module_name: 模块名，即 {ref}`nonebot.plugin.model.Plugin.module_name`。
    """
    loaded = {plugin.module_name: plugin for plugin in _plugins.values()}
    has_parent = True
    while has_parent:
        if module_name in loaded:
            return loaded[module_name]
        module_name, *has_parent = module_name.rsplit(".", 1)


def get_loaded_plugins() -> Set["Plugin"]:
    """获取当前已导入的所有插件。"""
    return set(_plugins.values())


def get_available_plugin_names() -> Set[str]:
    """获取当前所有可用的插件名（包含尚未加载的插件）。"""
    return {
        plugin
        for plugin in chain.from_iterable(
            manager.available_plugins for manager in _managers
        )
        if isinstance(plugin, str)
    }


def get_available_plugin_fullpaths() -> Set[Tuple[str, ...]]:
    """获取当前所有可用的插件路径（包含尚未加载的插件）。"""
    return {
        plugin
        for plugin in chain.from_iterable(
            manager.available_plugins for manager in _managers
        )
        if isinstance(plugin, tuple)
    }


from .on import on as on
from .manager import PluginManager
from .on import on_type as on_type
from .model import Plugin as Plugin
from .load import require as require
from .on import on_regex as on_regex
from .on import on_notice as on_notice
from .on import on_command as on_command
from .on import on_keyword as on_keyword
from .on import on_message as on_message
from .on import on_request as on_request
from .on import on_endswith as on_endswith
from .load import load_plugin as load_plugin
from .on import CommandGroup as CommandGroup
from .on import MatcherGroup as MatcherGroup
from .on import on_fullmatch as on_fullmatch
from .on import on_metaevent as on_metaevent
from .load import load_plugins as load_plugins
from .on import on_startswith as on_startswith
from .load import load_from_json as load_from_json
from .load import load_from_toml as load_from_toml
from .model import PluginMetadata as PluginMetadata
from .on import on_shell_command as on_shell_command
from .load import load_all_plugins as load_all_plugins
from .load import load_builtin_plugin as load_builtin_plugin
from .load import load_builtin_plugins as load_builtin_plugins
from .load import inherit_supported_adapters as inherit_supported_adapters
