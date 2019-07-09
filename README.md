# A simple registration program
This program is still highly WIP

## Usage
This program was designed as simple login/register system
It is written as a console application

After start, you are provided with 3 options

> Welcome to RegSys Software, created by Koumakpet <koumakpet@hexadynamic.com> <br>
>   ->Login:            1 <br>
>   ->Register:         2 <br>
>   ->Exit/Go back:     * <br>

If you choose a wrong option, you can use `*` to go back

### Register
> -Register- <br>
> Enter your email address: test@test.net <br>
> Enter your new username: test <br>
> Enter password: ************ <br>
> Re-Enter password: ************ <br>
> <br>
> Registered successfully <br>
> Press Enter to continue... <br>

Password requirements for registration are:
- 1 Uppercase letter
- 1 Lowercase letter
- 1 Number
- Minimum length of 7 characters

After successful registration, you will return to main menu
### Login
> -Login- <br>
> Enter your username: test <br>
> State your password: ************ <br>
>  <br>
> Logged in successfully <br>
> Press Enter to continue.. <br>

After you log-in, depending on your permission level (*user, admin, superadmin, developer*) you have access to diffirent options

> (Your permission level: user) <br>
> (Your Encrypted password: 567ca6093ffd6e77f3c8910a4100f89b1b812548abfcc3577e31c8ed) <br>
>  <br>
>  ->1: Change E-Mail address <br>
>  ->2: Change password <br>
>  ->3: Log-out <br>
>  <br>
> Enter action number: <br>

There is a pre-created admin account with super-admin permission level <br>
Default credentials for this account are:
```
 Name: admin
 Password: admin
```
From this account, you can  <br>
- Create new users with higher permission levels (*user, admin, superadmin*) <br>
- Remove other accounts (*within your permission level*) <br>
- Edit existing users data (*within your permission level*) <br>

> -Welcome admin- <br>
>  <br>
> (Your current E-Mail: None set) <br>
> (Your permission level: superadmin) <br>
> (Your Encrypted password: 58acb7acccce58ffa8b953b12b5a7702bd42dae441c1ad85057fa70b) <br>
>  <br>
>  ->1: Create new user <br>
>  ->2: Remove existing user<br>
>  ->3: Edit existing user <br>
>  ->4: Change your E-Mail address <br>
>  ->5: Change your password <br>
>  ->6: Log-out <br>
>  <br>
> Enter action number:<br>
