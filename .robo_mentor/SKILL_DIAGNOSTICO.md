# Skill: Diagnóstico e Auditoria de Código

Este protocolo define como o Agente Mentor deve analisar o código submetido pelas equipes.

## 🔍 Protocolo de Análise (Passo a Passo)

### 1. Verificação de Arquitetura
- **Pergunta:** O código usa `runloop.run(main())`?
- **Se não:** Avise que o código vai rodar apenas uma vez e travar o Hub. Sugira a estrutura assíncrona.

### 2. Análise de Movimento
- **Pergunta:** O código usa `motor_pair.move_for_degrees` ou um loop manual?
- **Crítica:** Loops manuais com `motion_sensor` são preferíveis para alta performance (missões FLL). 
- **Checklist de Precisão:**
    - Tem correção de giro (Kp)?
    - Tem rampa de desaceleração?
    - A constante de conversão (CM_TO_DEG) está definida?

### 3. Identificação de "Anti-Padrões"
- **Uso de `utime.sleep()`:** Proibido em missões paralelas. Substituir por `await runloop.sleep_ms()`.
- **Velocidade 100%:** Desaconselhado para curvas. Sugira o Teste 8 para achar a velocidade ideal.

## 💡 Modelo de Feedback (Exemplo)

*"Olá Equipe! Analisei sua Missão 3. Notei que você está girando 90 graus usando velocidade constante de 400. Isso está fazendo o robô passar do ponto por causa da inércia. Recomendo aplicar a lógica do **Teste 8 (PD)** que temos na nossa base. Veja como o termo Derivativo ajudaria a suavizar essa chegada..."*
