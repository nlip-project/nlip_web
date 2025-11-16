//const { spawn } = require('node:child_process');
/*
import { spawn } from 'node:child_process'

export async function runModule(search_term) {
    const path = "../../website_modules/dellelce_bookstore_module.py"

    const program = spawn('python', [path, search_term])

    let data = ''

    program.stdout.on('data', (stdout) => {
        data += stdout.toString()
    })

    // When script is finished, print collected data
    program.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
        console.log(data);
    });
}
*/