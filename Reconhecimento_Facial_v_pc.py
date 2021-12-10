

# Bibliotecas
import cv2 as cv
import numpy as np
import dlib
import RPi.GPIO as gpio
import time

# Codigo de cores RGB
azul = (255, 0, 0)

# Configurando como BCM (digital) ou BOARD(numero da placa)
gpio.setmode(gpio.BOARD)

# Configurando portas como entrada ou saída
gpio.setup(12, gpio.OUT) # motor roda esquerda - PIN12 PWM0
gpio.setup(18, gpio.OUT) # motor roda direita - PIN18 PWM0
gpio.setup(13, gpio.OUT) # motor ré roda esquerda - PIN13 PWM1
gpio.setup(19, gpio.OUT) # motor ré roda direita - PIN19 PWM1

# Configurando PWM de saídas para os motores
pwm_esq = gpio.PWM(12,127) 
pwm_dir = gpio.PWM(18,127) 
#pwm_esq_re = gpio.PWM(13,127) 
#pwm_dir_re = gpio.PWM(19,127) 

# configurando para ativar/desligar as saídas PWM
ativar_motor_esq = pwm_esq.start(0)
ativar_motor_dir = pwm_dir.start(0)
#ativar_motor_esq_re = pwm_esq_re.start(0)
#ativar_motor_dir_re =pwm_dir_re.start(0)

desligar_motor_esq = pwm_esq.stop(0)
desligar_motor_dir = pwm_dir.stop(0)
#desligar_motor_esq_re = pwm_esq_re.stop(0)
#desligar_motor_dir_re =pwm_dir_re.stop(0)

# Comandos de movimentação

def acelerar(p62, p66, p37, p43, p44, p46, p47, p19, p24, p50, p51, p52, p32, p33, p34, p1, p15):
    if p66.y - p62.y > 5:
        ativar_motor_esq
        ativar_motor_dir
        print("Cadeira acelerando!")

    elif (p37.y - p19.y) + (p44.y - p24.y) > 46:
        print("Movimento para tras")
        
    elif p1.y - p15.y > 40:
        ativar_motor_esq
        desligar_motor_dir
        print("Girando para direita")    
        
    elif p1.y - p15.y < -40:    
        ativar_motor_dir
        desligar_motor_esq
        print("Girando para esquerda")

    else:
        desligar_motor_dir
        desligar_motor_esq
        print("Cadeira parada")

# Leitura do Video da Camera
camera = cv.VideoCapture(0)

# Usando o detector de faces da biblioteca dlib para identificar os rostos
detector = dlib.get_frontal_face_detector()
    
# Usando o predictor composto por 68 pontos do rosto 
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Iniciando a operação com motores desligados
desligar_motor_dir
desligar_motor_esq

# Chaves de segurança
habilita_operacao = 0
habilitador = 1
desliga = 0

while True:
    
    # leitura de cada imagem captada pela camera
    ret, frame = camera.read()
    
    # Caso nehuma imagem seja captada pela camera
    if not ret:
        print("Nenhuma imagem captada!")
        break
    
    # Transformando imagens para escala cinza
    img_cinza = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Armazendando os rostos na imagem de escala cinza
    rostos = detector(img_cinza)

    # Identificação do rosto no video 
    for rosto in rostos:
        x1 = rosto.left()
        y1 = rosto.top()
        x2 = rosto.right()
        y2 = rosto.bottom()
        
        # Identifica o rosto na camera e sinaliza com um retangulo
        #cv.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 3)
        
        # Determina a matriz de pontos de cada rosto em escala cinza
        pontos = predictor(img_cinza, rosto) 

        # Define pontos da boca
        labio_sup = pontos.part(62)
        labio_inf = pontos.part(66)
        
        # Define pontos do olho direito
        p37 = pontos.part(37)
        p38 = pontos.part(38)
        p40 = pontos.part(40)
        p41 = pontos.part(41)

        # Define pontos do olho esquerdo
        p43 = pontos.part(43)
        p44 = pontos.part(44)
        p46 = pontos.part(46)
        p47 = pontos.part(47)

        #Define sobrancelha
        p19 = pontos.part(19)
        p24 = pontos.part(24)

        # Define Distancia entre boca e nariz (bico)
        p50 = pontos.part(50)
        p51 = pontos.part(51)
        p52 = pontos.part(52)
        p32 = pontos.part(32)
        p33 = pontos.part(33)
        p34 = pontos.part(34)
        
        # Define distancia entre maxilares
        p1 = pontos.part(1)
        p15 = pontos.part(15)

        # Sistema de segurança - Habilitando a operação baixando sobrancelhas
        if habilitador == 1:
            if (p37.y - p19.y + p44.y - p24.y) < 28: 
                habilita_operacao = 1
                print("Operacao por expressoes faciais habilitada!")
                habilitador = 0
                desliga = 1
                
        # Sistema de segurança - Desativando a operação com bico                
        if desliga == 1:       
            if (p50.y - p32.y) + (p51.y - p33.y) + (p52.y - p34.y) <= 40:
                habilita_operacao = 0
                print("Operacao por expressoes faciais desativada!")
                habilitador = 1
                desliga = 0               
        
        # Chamada de funções de movimentação
        if habilita_operacao == 1:
            acelerar(labio_sup, labio_inf, p37, p43, p44, p46, p47, p19, p24, p50, p51, p52, p32, p33, p34, p1, p15)


        # Desenha na camera os 68 pontos do rosto em forma de circulos de raio r pixels
        r = 1
        for p in range(0, 68):
            x = pontos.part(p).x
            y = pontos.part(p).y
            cv.circle(frame, (x, y), r, azul, -1)
            
        
    # Comando para desativar a camera e sair do laço de repetição
    cv.imshow('Video - Pressione "D" para desativar', frame)
    
    if cv.waitKey(20) & 0xFF == ord('d'):
        break

camera.release()
cv.destroyAllWindows() 