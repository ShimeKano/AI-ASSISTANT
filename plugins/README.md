# Plugins

New capabilities should be added as isolated `Tool` implementations and registered with `ToolRegistry`.

The core brain never imports a concrete feature. This keeps new features replaceable and prevents feature code from spreading through the application.

Future plugin discovery can load packages dynamically and call `registry.register()` without changing the Brain.
