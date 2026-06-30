# Migração dos modelos IFC para Git LFS

## Por que e o estado atual

Os arquivos `HVG_MASTER_v*.ifc` têm ~53–56 MB cada (≈ 364 MB no total do
histórico), acima do limite recomendado de 50 MB do GitHub — daí o aviso
`GH001: Large files detected` a cada push.

A migração para **Git LFS** (Large File Storage) resolve isso, guardando os
binários grandes fora do histórico Git e versionando apenas ponteiros de texto.

> **Limitação do ambiente de geração:** o ambiente *Claude Code on the web* onde
> estes modelos foram criados tem o endpoint `lfs.github.com` **bloqueado por
> política de rede** (CONNECT 403). Por isso a migração foi **preparada** (script
> e instruções) mas **não pôde ser concluída** a partir de lá — o upload dos
> objetos LFS precisa ser feito de um ambiente com acesso ao GitHub LFS.

## Como concluir (na sua máquina)

1. Instale o `git-lfs` (https://git-lfs.com): `brew install git-lfs`
   (macOS) · `sudo apt-get install git-lfs` (Ubuntu) · incluso no Git for Windows.
2. Clone/atualize o repositório e selecione o branch:
   ```bash
   git checkout claude/bim-ifc-project-planning-gugw0t
   ```
3. Rode o script:
   ```bash
   bash scripts/setup_git_lfs.sh
   ```
   Ele oferece dois modos:

   | Modo | O que faz | Push |
   |------|-----------|------|
   | **A — Forward** | Move só os `.ifc` atuais para LFS, sem reescrever histórico | `git push` normal |
   | **B — Completa** | `git lfs migrate import` reescreve o histórico do branch movendo **todos** os `.ifc` para LFS (encolhe o repo) | `git push --force-with-lease` |

   - Use **A** se quer simplicidade e não se importa que os blobs antigos
     permaneçam no histórico.
     - Use **B** se quer realmente reduzir o tamanho do repositório (recomendado
     para este caso, dado o volume), ciente de que reescreve o histórico do
     branch e exige force-push.

## Conferência

```bash
git lfs ls-files          # lista os arquivos sob LFS
git lfs status
```

## Configuração aplicada

O rastreamento fica em `.gitattributes`:

```
*.ifc filter=lfs diff=lfs merge=lfs -text
```
