## Guide to configurate ET2

Thanks for choosing ET2. This is a guide to help you configurate this tool. All configration are place in `public` or `private` settings folder.

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