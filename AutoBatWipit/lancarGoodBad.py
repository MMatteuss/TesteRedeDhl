import pyautogui
import time
import keyboard
import pyperclip
import winsound
import os
import sys

clear = lambda: os.system('cls')

def limpar_console():
    clear()

def tocar_som_erro():
    winsound.MessageBeep(type=winsound.MB_ICONERROR)
    time.sleep(1)

def tocar_som_ok():
    winsound.MessageBeep(type=winsound.MB_OK)

def obter_modelo_e_sku():
    while True:
        try:
            print("Qual Bateria irá jogar?")
            print("1 - SP930")
            print("2 - L400")
            resposta = int(input("Digite o número 1 ou 2: "))
            if resposta == 1:
                return "SP930", "COM20250039"
            elif resposta == 2:
                return "L400", "COM20250006"
            else:
                print("Resposta inválida. Digite 1 ou 2.")
        except ValueError:
            print("Resposta inválida. Digite um número.")

def obter_tipo_operacao():
    while True:
        try:
            print("O que irá fazer:")
            print("1 - GOOD")
            print("2 - BAD")
            opcao = int(input("Digite 1 ou 2: "))
            if opcao == 1:
                return "Good", 1
            elif opcao == 2:
                return "Bad", 2
            else:
                print("Opção inválida.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

def obter_sub_lpn():
    while True:
        sub = input("Digite a Sub-LPN que irá utilizar: ").strip()
        if sub:
            return sub
        print("Sub-LPN não pode ser vazia. Tente novamente.")

def exibir_informacoes_inicio(tipo, modelo, sub_lpn):
    limpar_console()
    print("Iniciando código...")
    print(f"Fazendo: {tipo} {modelo}, jogando na Sub: {sub_lpn}")
    time.sleep(3)

def verificar_texto():
    """Retorna 'sku', 'Triage' ou 'invalid_serial' baseado no texto copiado (agora mais robusto)."""
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')
    pyautogui.hotkey('ctrl', 'c')
    texto = pyperclip.paste()
    
    texto_normalizado = ' '.join(texto.split()).lower()
    
    if "inserir sku" in texto_normalizado:
        return "sku"
    elif "serial number is not valid" in texto_normalizado:
        tocar_som_erro()
        return "Triage"
    elif "triage order initiation" in texto_normalizado:
        return "Triage"
    else:
        return None

def tratar_serial_invalido():
    print("'Serial Number is not valid' detectado! Executando correção...")
    pyautogui.hotkey('alt', 'left')
    time.sleep(0.3)
    pyautogui.click(383, 552)
    pyautogui.hotkey('ctrl', 'a')
    keyboard.wait('enter')
    print("Correção concluída.")

def obter_defeito():
    menu_defeitos = """
1 - Bateria Danificada
2 - Conector Bateria Danificado
3 - Cabo Bateria Danificado
4 - Involucro Bateria Avariado
5 - Involucro Bateria Sujo
6 - Identificação Bateria Comprometida
7 - Bateria Desconhecida
8 - Bateria Descarregada
9 - Bateria aprovada - funcional
10 - Recarga bateria - Aprovado funcional
11 - Recarga bateria - Reprovado funcional
12 - Bateria reprovada - Funcional
13 - Bateria Obsoleta
"""
    print("Qual é o defeito da bateria:")
    print(menu_defeitos)
    while True:
        try:
            valor = int(input("Digite o número do defeito: "))
            if 1 <= valor <= 13:
                return valor
            else:
                print("Valor inválido. Digite um número entre 1 e 13.")
        except ValueError:
            print("Entrada inválida. Digite apenas o número.")

def executar_ciclo_good(sku, sub_lpn):
    exibir_informacoes_inicio("Good", modeloBateria, sub_lpn)
    print("Script: primeiro clique (após 5s), pressione ENTER para começar a verificação.")
    print("Loop infinito. Ctrl+C para interromper.\n")
    time.sleep(5)

    estado = None
    while True:
        while estado != "Triage":
            time.sleep(0.1)
            estado = verificar_texto()
            if estado == "invalid_serial":
                tratar_serial_invalido()
                estado = None
                continue
            if estado == "Triage":
                break

        if estado == "Triage":
            pyautogui.press('down')
            tocar_som_ok()
            pyautogui.click(383, 552)
            keyboard.wait('enter')

        while True:
            estado = verificar_texto()
            if estado == "invalid_serial":
                tratar_serial_invalido()
            elif estado == "sku":
                break
            elif estado == "Triage":
                break
            else:
                time.sleep(0.1)

        if estado == "Triage":
            continue

        # Preenche os dados
        pyautogui.click(383, 552)
        pyautogui.write(sku)
        pyautogui.hotkey('tab')
        pyautogui.write("no")
        pyautogui.hotkey('tab')
        pyautogui.write(sub_lpn)
        pyautogui.hotkey('enter')
        time.sleep(0.1)
        pyautogui.hotkey('enter')
        time.sleep(0.1)
        print("Ciclo concluído.")

def executar_ciclo_bad(sku, lpn):
    defeito_num = obter_defeito()
    exibir_informacoes_inicio("Bad", modeloBateria, lpn)
    print(f"Defeito selecionado: {defeito_num} -> serão pressionados {defeito_num} TAB(s).\n")
    time.sleep(5)

    estado = None
    while True:
        while estado != "Triage":
            time.sleep(0.1)
            estado = verificar_texto()
            if estado == "invalid_serial":
                tratar_serial_invalido()
                estado = None
                continue
            if estado == "Triage":
                break

        if estado == "Triage":
            pyautogui.press('down')
            tocar_som_ok()
            pyautogui.click(383, 552)
            keyboard.wait('enter')

        while True:
            estado = verificar_texto()
            if estado == "invalid_serial":
                tratar_serial_invalido()
            elif estado == "sku":
                break
            elif estado == "Triage":
                break
            else:
                time.sleep(0.1)

        if estado == "Triage":
            continue

        pyautogui.click(383, 552)
        pyautogui.write(sku)
        pyautogui.hotkey('tab')
        pyautogui.write("yes")
        pyautogui.hotkey('tab')
        pyautogui.write(lpn)
        time.sleep(1.3)
        pyautogui.click(550, 790)
        time.sleep(0.3)

        print(f"Pressionando {defeito_num} TAB(s) para selecionar o defeito...")
        pyautogui.press('tab', presses=defeito_num)
        pyautogui.hotkey('space')
        time.sleep(0.1)

        pyautogui.hotkey('enter')
        time.sleep(0.1)
        pyautogui.hotkey('enter')
        time.sleep(0.1)
        print("Ciclo concluído.")
        time.sleep(1)

def menu_interrupcao(tipo_operacao, sub_lpn_atual):
    limpar_console()
    print("\nInterrupção solicitada (Ctrl+C).")
    print(f"Operação atual: {tipo_operacao}")
    print(f"Sub-LPN atual: {sub_lpn_atual}")
    print("\nO que deseja fazer?")
    print("1 - Finalizar o programa")
    print("2 - Fazer {} com outra Sub-LPN".format(tipo_operacao))
    print("3 - Iniciar o código do zero")
    while True:
        try:
            escolha = int(input("Digite o número (1 a 3): "))
            if escolha == 1:
                return 'sair'
            elif escolha == 2:
                return 'nova_sub'
            elif escolha == 3:
                return 'reiniciar'
            else:
                print("Opção inválida. Digite 1, 2 ou 3.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

def main():
    while True: 
        try:
            # Seleção inicial do tipo de bateria
            global modeloBateria, sku
            modeloBateria, sku = obter_modelo_e_sku()

            # Seleção da operação (Good/Bad)
            tipo_operacao, cod_operacao = obter_tipo_operacao()

            # Seleção da sub-LPN
            sub_lpn = obter_sub_lpn()
            limpar_console()

            # Loop principal para trocar apenas a sub-LPN (opção 2)
            while True:
                try:
                    if cod_operacao == 1:  # GOOD
                        executar_ciclo_good(sku, sub_lpn)
                    else:  # BAD
                        executar_ciclo_bad(sku, sub_lpn)

                except KeyboardInterrupt:
                    # Captura Ctrl+C dentro do ciclo
                    decisao = menu_interrupcao(tipo_operacao, sub_lpn)
                    if decisao == 'sair':
                        print("Encerrando programa.")
                        return
                    elif decisao == 'nova_sub':
                        sub_lpn = obter_sub_lpn()
                        limpar_console()
                        print(f"Continuando com a nova Sub-LPN: {sub_lpn}")
                        continue  # reinicia o while True com a nova sub
                    elif decisao == 'reiniciar':
                        print("Reiniciando o programa do zero...")
                        time.sleep(1)
                        limpar_console()
                        break  # sai do while interno, vai para o início do main

        except KeyboardInterrupt:
            # Captura Ctrl+C durante a configuração inicial
            decisao = menu_interrupcao("(nenhuma operação em andamento)", "")
            if decisao == 'sair':
                print("Encerrando programa.")
                return
            elif decisao == 'reiniciar':
                print("Reiniciando o programa do zero...")
                time.sleep(1)
                limpar_console()
                continue  # reinicia o loop externo
            else:  # 'nova_sub' não faz sentido aqui, trata como reinício
                print("Opção inválida para este estágio. Reiniciando...")
                continue

if __name__ == "__main__":
    main()