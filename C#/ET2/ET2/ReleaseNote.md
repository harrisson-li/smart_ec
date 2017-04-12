## v0.0.0.36

1. Use ectools to activate test account.
2. Save new test accounts to http://cns-qaauto5/test_accounts
3. You don't have to update host in your local machine to use this tool now.

## v0.0.0.35

1. Bug fix: use python.exe from PATH environment variable but not shell.

## v0.0.0.34

1. Add white list feature, only people in white list can access live environment.

## v0.0.0.33

1. Support new tokens for quick actions: $school, $level, $productId, $accountType

## v0.0.0.32

1. The E10/S15/S15_V2 checkbox is for account type now, but not service version.
2. Activate S15 account with V2 service by default.

## v0.0.0.31

1. Open help page instead of a useless dialog.
2. Sort and align quick actions by name.

## v0.0.0.30

1. Change deployment location to lab server.

## v0.0.0.28

1. Layout changed, now you can add more quick actions.

## v0.0.0.27

1. Fix typo in useful link.
2. Support `$partner` token in URL.
3. Separete debug log to another file.
4. Wait for quick action sync completed then start the application.

## v0.0.0.26 - Preview

1. Fix bug - remember last 20 but not first 20 test accounts.
2. Append ctr and partner when generating test account but not activating account.
3. Keep console window and shows output for python quick actions.

## v0.0.0.23 - Preview

1. Fix bug - need to click twice to open a link.
2. Fix bug - product filter does not work well sometimes.
3. Quick actions are shared by all users now, local quick actions will be overwritten by public quick actions.
4. You need to define and publish quick actions to global settings folder.

## v0.0.0.21 - Preview

1. Able to resolve test account when input name or member id of student
2. Remember recent 20 generated test accounts, you can select from user name dropdown list.

## v0.0.0.19 - Preview

1. Support test account type: E10, S15 and S15 V2.0
2. Able to activate E10 test account.
3. Improve test account page, use flexible grid layout.

## v0.0.0.17 - Preview

1. Able to define quick actions, support `cmd` and `python` scripts
2. Fix silent crash issue.
3. Known issue: if host file is hidden, host editor will not work. (By Judy)
4. Switch test environment will refresh useful links now.

## v0.0.0.16 - Preview

1. Able to view full log by clicking status bar.
2. Add Test Environments: `LiveCN` and `LiveUS`.
3. Improve host editor, able to switch host according to profiles.
4. Implement a simple settings dialog.
5. Support more token in links: `$token`, `$mark`
6. Improve useful links tab loading speed.

## v0.0.0.14 - Preview

1. Implement useful link, add more links now.
2. Support tokens in links: `$id`, `$name`, `$env`
3. Remember your hits on each link.
4. Show release note for new version.

## v0.0.0.10 - Preview

1. Personal settings folder `%UserProfile%\ET2`
2. Global settings folder `\\cns-qaauto5\Shared\ET2\Settings`
3. If you want to run locally, create a global folder at `%UserProfile%\ET2_Global`

## v0.0.0.5 - Preview

1. Able to filter products according to product id or product name.
2. Able to get division code according to city and school name.

## v0.0.0.1 - Preview

1. Preview for account tool.
2. Preview for host editor.
3. Preview for useful link.