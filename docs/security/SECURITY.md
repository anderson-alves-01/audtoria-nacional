# Segurança, privacidade e soberania

## Modelo de autorização

RBAC define função; ABAC restringe por tenant, órgão, território, finalidade, classificação, horário, dispositivo e vigência. Toda consulta sensível exige `purpose_id` válido.

## Controles

- MFA, sessão curta e reautenticação para exportação.
- Criptografia TLS e chaves segregadas por instituição.
- Segredos em cofre gerenciado.
- DLP, mascaramento e minimização.
- Marca d'água e identificação do usuário em relatórios.
- Download e impressão condicionados à política.
- Logs imutáveis e alertas comportamentais.
- Backups criptografados e testes de restauração.
- SAST, DAST, SCA, secret scan, SBOM e pentest.

## IA

- Gateway único para modelos.
- Proibição de treinamento com dados institucionais.
- Coleções RAG segregadas.
- Recuperação filtrada pela autorização do usuário.
- Evidências citadas em cada resposta.
- Proteção contra prompt injection e exfiltração.
- Aprovação humana antes de parecer, autuação ou comunicação externa.

## LGPD e cadeia de custódia

Registrar finalidade, necessidade, base legal, origem, acesso, transformação, exportação, retenção e descarte. Evidências possuem hash, carimbo de tempo, versão e histórico de custódia.

