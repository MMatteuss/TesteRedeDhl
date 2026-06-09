# pip install pytesseract pandas opencv-python numpy pyautogui mss

import cv2
import numpy as np
import pyautogui
import mss
import pandas as pd
import time
import os
import pytesseract  # necessário para ler o Order Number

# ================== CONFIGURAÇÕES ==================
# Caminho para o executável do Tesseract (no Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # ajuste se necessário

# Diretório das imagens de referência (mesmo local do script)
os.chdir(os.path.dirname(__file__))

# Limiar de confiança para template matching (0 = baixo, 1 = alto)
CONFIANCA = 0.7
# Tempo de espera padrão entre ações
ESPERA_PADRAO = 0.5

# ================== FUNÇÕES AUXILIARES ==================
def esperar_carregamento():
    """Verifica se a imagem 'carregamento.png' está na tela. Enquanto estiver, aguarda 1s."""
    print("🔍 Verificando tela de carregamento...")
    while True:
        # captura a tela
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            tela = np.array(sct.grab(monitor))
            tela_cinza = cv2.cvtColor(tela, cv2.COLOR_BGRA2GRAY)
        # carrega o template de carregamento
        template = cv2.imread('carregamento.png', cv2.IMREAD_GRAYSCALE)
        if template is None:
            print("⚠️ Imagem 'carregamento.png' não encontrada. Ignorando verificação de loading.")
            break
        resultado = cv2.matchTemplate(tela_cinza, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(resultado)
        if max_val < CONFIANCA:
            break
        print("⏳ Carregando... aguardando 1 segundo.")
        time.sleep(1)
    print("✅ Carregamento concluído ou não detectado.")

def encontrar_e_clicar(imagem, confianca=CONFIANCA, clicar=True):
    """
    Procura a imagem na tela. Se encontrar, clica no centro (opcional) e retorna a posição (x, y) central.
    Retorna None se não encontrar.
    """
    esperar_carregamento()  # antes de qualquer ação, garante que não há loading
    template = cv2.imread(imagem, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"❌ ERRO: Arquivo '{imagem}' não encontrado.")
        return None
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        tela = np.array(sct.grab(monitor))
        tela_cinza = cv2.cvtColor(tela, cv2.COLOR_BGRA2GRAY)

    h, w = template.shape
    resultado = cv2.matchTemplate(tela_cinza, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(resultado)

    if max_val >= confianca:
        x, y = max_loc
        centro = (x + w//2, y + h//2)
        if clicar:
            pyautogui.click(centro)
            print(f"✅ Clicado em {imagem} com {max_val*100:.1f}% de confiança")
            time.sleep(ESPERA_PADRAO)
        return centro
    else:
        print(f"❌ Imagem '{imagem}' não encontrada (max conf: {max_val*100:.1f}%)")
        return None

def encontrar_todos_os_botoes(imagem, confianca=CONFIANCA):
    """Retorna uma lista com os centros (x, y) de todas as ocorrências da imagem na tela."""
    esperar_carregamento()
    template = cv2.imread(imagem, cv2.IMREAD_GRAYSCALE)
    if template is None:
        return []
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        tela = np.array(sct.grab(monitor))
        tela_cinza = cv2.cvtColor(tela, cv2.COLOR_BGRA2GRAY)

    h, w = template.shape
    resultado = cv2.matchTemplate(tela_cinza, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(resultado >= confianca)
    centros = []
    for pt in zip(*loc[::-1]):
        centros.append((pt[0] + w//2, pt[1] + h//2))
    # Remove duplicatas próximas (caso o mesmo botão seja detectado mais de uma vez)
    centros_unicos = []
    for c in centros:
        if not any(abs(c[0]-u[0]) < 10 and abs(c[1]-u[1]) < 10 for u in centros_unicos):
            centros_unicos.append(c)
    return centros_unicos

def obter_order_number_proximo_a(x, y, offset_esquerda=-200, largura=300, altura=30):
    """
    Captura uma região à esquerda do ponto (x, y) (onde está o botão Cancelar)
    e tenta ler o texto (Order Number) usando OCR.
    Ajuste os offsets conforme a interface real.
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        # Região: começando em (x + offset_esquerda, y - altura//2) até largura x altura
        reg_x = x + offset_esquerda
        reg_y = y - altura//2
        # Garantir que a região não saia da tela
        reg_x = max(reg_x, 0)
        reg_y = max(reg_y, 0)
        regiao = {
            'left': reg_x,
            'top': reg_y,
            'width': largura,
            'height': altura,
            'mon': 1
        }
        img = sct.grab(regiao)
        img_np = np.array(img)
        img_cinza = cv2.cvtColor(img_np, cv2.COLOR_BGRA2GRAY)
        # Aplica OCR
        texto = pytesseract.image_to_string(img_cinza, config='--psm 7').strip()
        if texto:
            print(f"📝 Order Number lido: '{texto}'")
            return texto
        else:
            print(f"⚠️ Não foi possível ler Order Number próximo a ({x}, {y})")
            return None

# ================== FLUXO PRINCIPAL ==================
def processar_serial(serial):
    print(f"\n🔹 Iniciando processamento do serial: {serial}")

    # 1. Clicar no campo de busca e digitar o serial
    pos_input = encontrar_e_clicar('input.png')
    if not pos_input:
        print("❌ Campo de busca não encontrado. Abortando este serial.")
        return
    pyautogui.write(serial)
    time.sleep(0.5)

    # 2. Clicar no botão Pesquisar
    if not encontrar_e_clicar('botaoPesquisar.png'):
        print("❌ Botão Pesquisar não encontrado. Abortando.")
        return

    # 3. Aguardar resultados (a tela de resultados deve aparecer)
    esperar_carregamento()
    time.sleep(1)  # tempo extra para a tabela se estabilizar

    # 4. Coletar todos os botões de cancelar (dos dois tipos)
    botoes_cancel = []
    for img in ['botaoCancel1.png', 'botaoCancel2.png']:
        botoes_cancel.extend(encontrar_todos_os_botoes(img))
    # Ordenar por Y (de cima para baixo) para processar na ordem da tabela
    botoes_cancel.sort(key=lambda p: p[1])
    print(f"🔢 Encontrados {len(botoes_cancel)} botões de cancelar.")

    # 5. Para cada botão, realizar o cancelamento
    for idx, (x, y) in enumerate(botoes_cancel, 1):
        print(f"\n  --- Cancelamento {idx} de {len(botoes_cancel)} ---")
        # 5a. Obter o Order Number da mesma linha (à esquerda do botão)
        # Ajuste os parâmetros conforme necessário:
        # offset_esquerda: quantos pixels à esquerda do botão está o texto do Order Number
        # largura: largura da região a ser capturada
        # altura: altura da linha
        order_number = obter_order_number_proximo_a(x, y, offset_esquerda=-300, largura=280, altura=25)
        if not order_number:
            print("⚠️ Não foi possível obter o Order Number. Pulando este cancelamento.")
            continue

        # 5b. Clicar no botão Cancelar
        pyautogui.click(x, y)
        time.sleep(0.5)
        esperar_carregamento()

        # 5c. Localizar o campo input02.png e digitar/colar o Order Number
        pos_input02 = encontrar_e_clicar('input02.png')
        if not pos_input02:
            print("❌ Campo input02 não apareceu. Cancelamento pode ter falhado.")
            continue

        # Digitar o Order Number (ou usar Ctrl+V se já copiado)
        pyautogui.write(order_number)
        time.sleep(0.3)
        # Pressionar Enter para confirmar (ou clique em OK, dependendo da interface)
        pyautogui.press('enter')
        print(f"✅ Order Number '{order_number}' inserido e confirmado.")
        esperar_carregamento()
        time.sleep(1)  # aguarda processamento do sistema

    print(f"✅ Todos os cancelamentos para o serial {serial} foram processados.\n")

# ================== INÍCIO DO PROGRAMA ==================
if __name__ == "__main__":
    # Ler a planilha
    try:
        df = pd.read_excel('dados.xlsx')
        if 'serial' not in df.columns:
            print("❌ A planilha não possui a coluna 'serial'.")
            exit()
        seriais = df['serial'].dropna().tolist()
        print(f"📄 Carregados {len(seriais)} seriais da planilha.")
    except Exception as e:
        print(f"❌ Erro ao ler planilha: {e}")
        exit()

    # Para cada serial, executar o fluxo
    for serial in seriais:
        processar_serial(str(serial))
        # Opcional: pausa entre seriais para reiniciar o estado da tela
        time.sleep(2)

    print("🏁 Automação finalizada.")