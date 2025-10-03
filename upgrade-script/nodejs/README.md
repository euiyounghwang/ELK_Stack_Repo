<i> 
Node.js is an open-source, cross-platform JavaScript runtime environment.

- Navigate to the official Node.js website (nodejs.org).
- Download the recommended LTS (Long Term Support) version installer for your operating system (Windows, macOS, or Linux).
- Run the downloaded installer and follow the on-screen prompts.
- Accept the license agreement and choose the installation location (the default is usually fine).
- Ensure that the "Add to PATH" option is selected during installation, as this allows you to run Node.js commands directly from your terminal or command prompt.
- Complete the installation process.

## NodeJS Setup
- This command should display the installed Node.js version, confirming a successful installation.: `node -v`
- This command should display the installed npm version.: `npm -v`
(Optional) Initialize a Node.js Project:
- Create a new directory for your project.
- Navigate into that directory in your terminal.
- Run the following command to initialize a new Node.js project: : `npm init`
- (Optional) Install Packages: Once your project is initialized, you can install additional packages using npm. For example, to install Express.js: `npm install express`

## NodeJS Run
- Run an exmple code: `node ./app.js`
```bash
Hello, Node.js!
```
- Run es client
    - npm init
    ```bash
    $ npm init
    This utility will walk you through creating a package.json file.
    It only covers the most common items, and tries to guess sensible defaults.

    See `npm help init` for definitive documentation on these fields
    and exactly what they do.

    Use `npm install <pkg>` afterwards to install a package and
    save it as a dependency in the package.json file.

    Press ^C at any time to quit.
    package name: (nodejs) node_es_client
    version: (1.0.0)
    description: es_client with a ssl certificate for the connection                                                                            
    entry point: (app.js) es_client.js
    test command:                                                                                                                               
    git repository:                                                                                                                             
    keywords:                                                                                                                                   
    author:                                                                                                                                     
    license: (ISC)                                                                                                                              
    About to write to C:\Users\euiyoung.hwang\Git_Workspace\ELK_Stack_Repo\upgrade-script\nodejs\package.json:

    {
    "name": "node_es_client",
    "version": "1.0.0",
    "description": "es_client with a ssl certificate for the connection",
    "main": "es_client.js",
    "scripts": {
        "test": "echo \"Error: no test specified\" && exit 1"
    },
    "author": "",
    "license": "ISC"
    }


    Is this OK? (yes) yes
    ```
    - npm install dotenv
    - `node ./node_es_client.js`
    ```bash    
    [dotenv@17.2.3] injecting env (7) from ..\csharp\esclient\.env -- tip: 🔑 add access controls to secrets: https://dotenvx.com/ops
    envInfo: This is a .env file
    ```