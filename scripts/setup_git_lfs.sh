#!/usr/bin/env bash
#
# Migração dos modelos IFC do HVG Inhotim para Git LFS.
#
# IMPORTANTE: rode este script NA SUA MÁQUINA (ou em qualquer ambiente com
# acesso de rede a lfs.github.com). O ambiente Claude Code on the web em que o
# modelo foi gerado tem o endpoint lfs.github.com BLOQUEADO por política de rede
# (CONNECT 403), portanto o push de objetos LFS não pode ser feito de lá.
#
# Pré-requisitos: git >= 2.x e git-lfs instalado (https://git-lfs.com).
#   macOS:   brew install git-lfs
#   Ubuntu:  sudo apt-get install git-lfs
#   Windows: incluído no Git for Windows
#
set -euo pipefail

BRANCH="${1:-claude/bim-ifc-project-planning-gugw0t}"

echo ">> Inicializando Git LFS"
git lfs install

echo ">> Rastreando *.ifc"
git lfs track "*.ifc"
git add .gitattributes
git commit -m "Configura Git LFS para *.ifc" || echo "(.gitattributes ja commitado)"

echo
echo "Escolha o modo de migração:"
echo "  [A] FORWARD  — converte apenas os arquivos atuais (sem reescrever historico)."
echo "                 Simples, sem force-push. Os blobs antigos continuam no historico."
echo "  [B] COMPLETA — reescreve o historico do branch movendo TODOS os .ifc para LFS"
echo "                 (git lfs migrate import). Encolhe o repo, mas EXIGE force-push."
read -r -p "Modo [A/B]: " MODE

case "${MODE^^}" in
  A)
    echo ">> Modo FORWARD: reconvertendo os .ifc atuais"
    git rm --cached -q $(git ls-files "*.ifc")
    git add $(git ls-files -c -o --exclude-standard "*.ifc"; ls *.ifc 2>/dev/null) .gitattributes
    git commit -m "Converte modelos .ifc atuais para Git LFS"
    git push origin "$BRANCH"
    ;;
  B)
    echo ">> Modo COMPLETA: reescrevendo historico do branch $BRANCH"
    git lfs migrate import --include="*.ifc" --include-ref="refs/heads/$BRANCH"
    echo ">> Force-push (historico reescrito)"
    git push --force-with-lease origin "$BRANCH"
    ;;
  *)
    echo "Opcao invalida. Abortado."; exit 1 ;;
esac

echo
echo ">> Concluido. Conferencia:"
git lfs ls-files | sed 's/^/   /'
