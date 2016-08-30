﻿## Guide to configurate ET2

Thanks for choosing ET2. This is a guide to help you configurate this tool. All configration are placed in `public` or `private` settings folder.

### 1. Public Settings Folder

Default set to `\\cns-fileserver1\Departments\11 Public\EFEC\ET2\Settings`, you can find configurations about environments, products, userful links and hosts data over there. **Changes in public settings** will impact all ET2 users.

> Tips: Copy public setting file to private settings folder can overrite it without impact others.

### 2. Private Settings Folder

Default set to `%UserProfile%\ET2`, you can see application saved state and private hosts folder at here.

### 3. Public Configurations

- Environments.csv (Test environments settings)
- ProductList.csv (Smart proudct data, to activate test account)
- DivisionCode.csv (Division code list, to activate test account)
- UsefulLinks.csv (Data file for useful links tab)
- FixLinks.csv (Data file to fix links if token replacement does not work)
- Hosts(Folder to place public host settings)

### 4. Private Configrations

- Save.XXXX (State file to save XXXX, e.g. Save.CurrentTestAccount)
- Hosts (Folder to place private host settings)
- QuickActions (Folder to place quick actions)

### 5. Token Replacement

Token replacement is wildly used in ET2, you can set token in useful links or quick actions. Current we supported bellow tokens:

- $id (=> member id)
- $name (=> student name)
- $env (=> current test environment)
- $mark (=> current tet environment mark)
- $token (=> secrect token to submit score)

### 6. Quick Actions

You can define quick actions in '[**PublicSettings**]/QuickActions' folder. There is a sample action added by default.
Quick actions can be accessed throught ET2 main window, and they will be shared by all users.

Supported quick action types:

- Cmd
- Python
- Url
- Sql (Comming soon)

Tips:

1. You quick action file must be ended with `.action`
2. You can use program data in %UserProfile%\ET2 folder, they are json file, prefix is 'Save.xxx`
3. `AsAdmin` and `WatiForExit` in quick action config file are optional to set.