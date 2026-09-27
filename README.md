# 📁 Renomeador de Músicas para Pendrive

Este script automatiza a organização de arquivos `.mp3` e `.m4a` em um pendrive, convertendo os `.m4a` para `.mp3` e renomeando todas as músicas com numeração sequencial no formato `001 - Nome da Música.mp3`, `002 - Outra Música.mp3`, etc.

---

## 🛠️ Funcionalidades

- Converte automaticamente arquivos `.m4a` para `.mp3` (via `ffmpeg`) e remove o `.m4a` original após a conversão e renomeação terem sido concluídas com sucesso.
- Remove numeração antiga dos nomes dos arquivos (ex: `01 - Música.mp3`, `01.Música.mp3`).
- Renomeia os arquivos com uma nova numeração sequencial de 3 dígitos.
- Normaliza espaços duplicados ou sobrando no início/fim dos nomes (ex: `Música   Antiga  .mp3` → `Música Antiga.mp3`).
- Remove acentos e caracteres não-ASCII quando a opção `--remover-acentos` é usada — útil para aparelhos de som automotivo com suporte limitado a acentuação (ex: `Não Há Ou` → `Nao Ha Ou`).
- Mantém a ordem alfabética das músicas.
- **Modo simulação por padrão**: mostra o que seria feito sem alterar nenhum arquivo; só aplica as mudanças com a opção `--executar`.
- Usa arquivos temporários durante a renomeação para evitar que um arquivo sobrescreva outro no meio do processo.
- Detecta e recusa nomes duplicados (inclusive após a conversão de `.m4a` para `.mp3`) antes de alterar qualquer arquivo.
- Organiza de forma padronizada para facilitar a navegação em dispositivos de som, carros, etc.

---

## 📌 Pré-requisitos

- Python 3 instalado.
- **`ffmpeg` instalado e disponível no PATH** — necessário apenas se houver arquivos `.m4a` para converter.
- Músicas no formato `.mp3` e/ou `.m4a` salvas na raiz do pendrive (o script não varre subpastas).
- Biblioteca padrão do Python (não é necessário instalar pacotes externos).

---

## 🚀 Como usar

1. **Copie o script** (`organizar_sequencial.py`) para seu computador.
2. **Execute o script apontando para a pasta do pendrive**, passando o caminho como argumento:

   ```bash
   python3 organizar_sequencial.py /caminho/para/o/pendrive
   ```

   > Se nenhum caminho for informado, o script usa o caminho padrão configurado na constante `CAMINHO_PADRAO`, no topo do arquivo.

3. **Por padrão, o script roda em modo simulação** e não altera nada — ele apenas mostra no terminal o que seria feito:

   ```
   SIMULAÇÃO — nenhum arquivo será alterado:

   Converter: música antiga.m4a → música antiga.mp3
   música antiga.m4a → 001 - música antiga.mp3

   Para aplicar, execute novamente com a opção --executar.
   ```

4. **Conferida a simulação**, execute de verdade com a opção `--executar`:

   ```bash
   python3 organizar_sequencial.py /caminho/para/o/pendrive --executar
   ```

   O terminal exibirá o progresso:

   ```
   Convertido: música antiga.m4a → música antiga.mp3
   Renomeado: música antiga.mp3 → 001 - música antiga.mp3
   Removido: música antiga.m4a
   ```

### Opções disponíveis

| Opção | Descrição |
|---|---|
| `caminho` (posicional) | Pasta onde estão as músicas. Se omitido, usa `CAMINHO_PADRAO`. |
| `--executar` | Aplica as mudanças de fato. Sem essa opção, o script só simula. |
| `--remover-acentos` | Remove acentos e caracteres não-ASCII dos nomes finais (recomendado para aparelhos de som automotivo mais simples). |

Exemplo combinando as opções, para um pendrive que vai tocar no carro:

```bash
python3 organizar_sequencial.py /run/media/usuario/MUSIC --remover-acentos --executar
```

---

## 📂 Exemplo de antes e depois

**Antes:**
```
01 - Louvor.mp3
02. Forró.m4a
03 samba.mp3
Música   Antiga  .m4a
```

**Depois (sem `--remover-acentos`):**
```
001 - Louvor.mp3
002 - Forró.mp3
003 - samba.mp3
004 - Música Antiga.mp3
```

**Depois (com `--remover-acentos`):**
```
001 - Louvor.mp3
002 - Forro.mp3
003 - samba.mp3
004 - Musica Antiga.mp3
```

---

## ⚠️ Atenção

- O script modifica permanentemente os nomes dos arquivos, converte os `.m4a` para `.mp3` e **apaga os `.m4a` originais** depois que a conversão e a renomeação terminam com sucesso. Faça um backup se necessário.
- Certifique-se de que todos os arquivos estão na raiz da pasta informada (o script não funciona em subpastas).
- Arquivos com nomes repetidos após remoção da numeração (ou após a conversão de `.m4a` para `.mp3`) fazem o script parar com um erro, sem alterar nada — resolva a duplicidade antes de rodar novamente.
- Sem `ffmpeg` instalado, o script recusa rodar em modo `--executar` caso existam arquivos `.m4a` na pasta.

---

## 📄 Licença

Este projeto é livre para uso pessoal ou profissional. Sem garantia. Use por sua conta e risco.