import pg from 'pg';import {fileURLToPath} from 'node:url';import {createApp} from './app.js';
if(!process.env.DATABASE_URL||!process.env.NEON_AUTH_BASE_URL)throw Error('DATABASE_URL and NEON_AUTH_BASE_URL required');
const pool=new pg.Pool({connectionString:process.env.DATABASE_URL,max:5,idleTimeoutMillis:30000,connectionTimeoutMillis:15000});pool.on('error',e=>console.error('database_pool_error',e.code||e.name));
const app=createApp({pool,authURL:process.env.NEON_AUTH_BASE_URL,staticDir:fileURLToPath(new URL('../dist',import.meta.url))});const server=app.listen(process.env.PORT||3000,'0.0.0.0',()=>console.log('STP portal ready'));
process.on('SIGTERM',()=>server.close(async()=>{await pool.end();process.exit(0)}));
