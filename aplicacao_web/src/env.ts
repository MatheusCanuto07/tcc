import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
	MYSQL_HOST: {
		description: 'Host do MySQL',
		schema: (value) => value ?? '127.0.0.1'
	},
	MYSQL_PORT: {
		description: 'Porta do MySQL',
		schema: (value) => value ?? '3307'
	},
	MYSQL_USER: {
		description: 'Usuário do MySQL',
		schema: (value) => value ?? 'tcc'
	},
	MYSQL_PASSWORD: {
		description: 'Senha do MySQL',
		schema: (value) => value ?? 'tcc_senha'
	},
	MYSQL_DATABASE: {
		description: 'Nome do banco',
		schema: (value) => value ?? 'tcc_contagem_ti'
	}
});
