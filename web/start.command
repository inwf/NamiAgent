#!/bin/bash
# macOS 双击运行：uv 同步依赖 → 启动网页端 → 自动打开浏览器
# 其他系统用：uv run --env-file .env python web/app.py（先在 .env 填写 API_KEY）
cd "$(dirname "$0")/.." || exit 1

if ! command -v uv >/dev/null 2>&1; then
  echo "需要先安装 uv，macOS 可以运行：brew install uv"
  echo "其他安装方式：https://docs.astral.sh/uv/getting-started/installation/"
  read -n 1
  exit 1
fi
if [ "${1:-}" != "--env-loaded" ]; then
  echo "用 uv 准备 Python、虚拟环境和运行依赖 ..."
  uv sync --locked --no-dev || { echo "安装依赖失败"; read -n 1; exit 1; }
  if [ -f .env ]; then
    # 让 uv 解析配置文件，再进入启动流程，API Key 和工作区都会生效。
    exec uv run --locked --no-dev --env-file .env bash web/start.command --env-loaded
  fi
fi

echo
echo "选择启动模式："
echo "  1) 演示模式（假模型，不需要 API Key）"
echo "  2) 真实模型（使用 .env 中的 API_KEY）"
while true; do
  printf "请输入 1 或 2（直接回车选 1）："
  read -r launch_mode
  launch_mode="${launch_mode:-1}"
  case "$launch_mode" in
    1|2) break ;;
    *) echo "请输入 1 或 2。" ;;
  esac
done

if [ "$launch_mode" = "2" ]; then
  if [ -z "$API_KEY" ]; then
    echo "真实模型需要 API Key，可以填写 .env，也可以现在粘贴。"
    printf "API Key（输入内容不会显示）: "
    read -r -s API_KEY
    printf '\n'
    API_KEY="$(printf '%s' "$API_KEY" | tr -d '[:space:]')"
  fi
  if [ -z "$API_KEY" ]; then
    echo "未填写 API Key，无法启动真实模型。请先在 .env 中填写 API_KEY。"
    exit 1
  fi
  export API_KEY
fi

# 默认使用当前目录；双击脚本时已进入 NamiAgent 根目录。
NAMI_WORKSPACE="${NAMI_WORKSPACE:-$PWD}"
mkdir -p "$NAMI_WORKSPACE" || exit 1
NAMI_WORKSPACE="$(cd "$NAMI_WORKSPACE" && pwd -P)" || exit 1
export NAMI_WORKSPACE
echo "工作区：$NAMI_WORKSPACE"

(sleep 2; open http://localhost:8765) &
if [ "$launch_mode" = "1" ]; then
  echo "启动演示模式 ..."
  uv run --locked --no-dev python web/app.py --demo
else
  echo "启动真实模型 ..."
  uv run --locked --no-dev python web/app.py
fi
