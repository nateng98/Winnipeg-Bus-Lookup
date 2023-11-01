# Winnipeg-Bus-Lookup
Making use of NodeJS and mySQL, this project establishes a comprehensive database for accessing Winnipeg bus schedules and weather information in the past, offering valuable insights into the impact of weather on public transportation efficiency in Winnipeg.

## Requirements
- MySQL
- NodeJS

## Configuration
- Connect to SQL Database: change server, username, password, database
```js
var config = {  
        server: 'your_server.database.windows.net',  //update me
        authentication: {
            type: 'default',
            options: {
                userName: 'your_username', //update me
                password: 'your_password'  //update me
            }
        },
        options: {
            // If you are on Microsoft Azure, you need encryption:
            encrypt: true,
            database: 'your_database'  //update me
        }
    };  
```
## How to run
1. git clone https://github.com/nateng98/Winnipeg-Bus-Lookup.git
2. cd
3. npm install
4. npm run start
5. Open in browser through local host

## Author
- <a href="">Emily Bond</a>
- <a href="https://github.com/nateng98">Nhat Anh Nguyen</a>
