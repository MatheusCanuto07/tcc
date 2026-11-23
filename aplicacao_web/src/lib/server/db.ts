import mysql from 'mysql2/promise';
import {
	MYSQL_DATABASE,
	MYSQL_HOST,
	MYSQL_PASSWORD,
	MYSQL_PORT,
	MYSQL_USER
} from '$app/env/private';

let pool: mysql.Pool | null = null;

/** Pool singleton para consultas ao MySQL do TCC. */
export function getPool(): mysql.Pool {
	if (!pool) {
		pool = mysql.createPool({
			host: MYSQL_HOST,
			port: Number(MYSQL_PORT),
			user: MYSQL_USER,
			password: MYSQL_PASSWORD,
			database: MYSQL_DATABASE,
			waitForConnections: true,
			connectionLimit: 8,
			namedPlaceholders: true,
			charset: 'utf8mb4'
		});
	}
	return pool;
}
