//import { config } from "dotenv";
import { defaultConfig } from "../config.js";
import { crawl, write } from "./core.js";
import { v4 as uuidv4 } from 'uuid';

//const uniqueId = uuidv4();
const id = process.env.school!
const configJson = process.env.CRAWLER_CONFIG;
if (!configJson) {
    throw new Error('CRAWLER_CONFIG environment variable is not set.');
}

const config = JSON.parse(configJson)
console.log(id)

await crawl(config,id);
await write(config,id);
