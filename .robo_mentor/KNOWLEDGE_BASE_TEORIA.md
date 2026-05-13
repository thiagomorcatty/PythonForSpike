# Base de Conhecimento: Os 15 Pilares da Precisão RoboNuvem

Este documento contém a fundamentação técnica e a justificativa para cada teste da biblioteca de calibração.

## 🟢 Nível 1: Fundamentos de Repetibilidade
### Teste 0: Diagnóstico e Reset
- **Teoria:** Sistemas robóticos precisam de um estado inicial conhecido.
- **Dica do Mentor:** Sempre alinhe fisicamente as rodas antes de rodar o Teste 0. Se o motor não estiver no zero absoluto, o PID terá um erro inicial.

### Teste 6: Multitarefa (Anexos)
- **Teoria:** Concorrência sem threads (Assincronia).
- **Dica do Mentor:** Nunca use `motor.run_for_degrees` para anexos enquanto o robô anda, pois ele bloqueia o loop. Use `motor.run()` com controle de tempo `utime.ticks_diff`.

## 🟡 Nível 2: Engenharia de Controle
### Teste 8: Giro PD (Proporcional-Derivativo)
- **Teoria:** O termo Proporcional (P) leva o robô ao alvo. O termo Derivativo (D) atua como um amortecedor, reduzindo a velocidade conforme o robô se aproxima do ângulo, evitando o "overshoot" (passar do ponto).
- **Dica do Mentor:** Se o robô oscila muito, aumente o Kd. Se ele demora a chegar, aumente o Kp.

### Teste 10: Perfil de Velocidade Trapezoidal
- **Teoria:** Controle de inércia. Aceleração gradual evita que as rodas deslizem no tapete liso da FLL. Frenagem gradual evita que o robô empine ou desalinhe na parada.
- **Dica do Mentor:** Em tapetes novos, use uma rampa de aceleração maior (30%). Em tapetes gastos, pode ser menor.

## 🔴 Nível 3: Diagnóstico Avançado
### Teste 13: Acúmulo de Erro Angular
- **Teoria:** Teste de estresse de odometria.
- **Dica do Mentor:** Se após 12 giros de 30° o robô não voltou para o zero, verifique o "Track Width" (distância entre rodas) no código.

### Teste 15: Figura em Oito
- **Teoria:** Teste de simetria mecânica.
- **Dica do Mentor:** Diferenças entre o círculo direito e esquerdo indicam motores com torque desigual ou fiação que está puxando o robô para um lado.
