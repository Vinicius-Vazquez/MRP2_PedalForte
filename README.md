# MRP II - Pedal Forte Bicicletas

Sistema de Planejamento dos Recursos de Manufatura (MRP II) desenvolvido em Python para a fábrica fictícia **Pedal Forte Bicicletas Ltda.** (Divinópolis - MG), no contexto da disciplina de Programação em Python do curso de Engenharia de Computação do CEFET-MG (Campus Divinópolis), sob orientação do Prof. Guido Pantuza.

## 1. Visão Geral do Projeto

O sistema substitui controles manuais em planilhas por um fluxo integrado de planejamento e controle da produção e estoques em um horizonte de **8 semanas**. A cada ciclo, o sistema apoia a tomada de decisão sobre o que produzir ou comprar, em quais quantidades, em quais semanas e com qual impacto sobre capacidade produtiva, estoques e custos padrão.

## 2. Arquitetura e Organização do Repositório

O projeto segue a organização modular definida para o sistema:

```text
MRP2_PedalForte/
├── main.py             # Ponto de entrada e ciclo de carregamento/salvamento de dados
├── menu.py             # Navegação em modo texto (menu principal e submenus)
├── itens.py            # Cadastro, listagem e alteração de itens (PA, SA, MP)
├── estrutura.py        # Cadastro e explosão indentada da estrutura de produto (BOM)
├── estoque.py          # Movimentações (entrada, saída, ajuste), saldos e Kardex
├── mps.py              # Gerenciamento do Plano Mestre de Produção (8 semanas)
├── mrp.py              # Explosão de necessidades e cálculo MRP
├── ordens.py           # Geração de OPs/OCs, controle de status e apontamento de produção
├── capacidade.py       # Centros de trabalho, roteiros e análise de Carga x Capacidade (CRP)
├── custos.py           # Cálculo recursivo de custo padrão (materiais + centro de trabalho)
├── relatorios.py       # Exportação de relatórios em CSV
├── graficos.py         # Geração e exibição de gráficos gerenciais com Matplotlib
├── persistencia.py     # Leitura e gravação de dados em JSON/CSV na pasta data/
├── utils.py            # Validações, formatação, leitura segura de entradas e helpers
└── data/               # Base de demonstração, histórico CSV, relatórios e gráficos gerados
```

## 3. Requisitos e Regras de Negócio Atendidos

### Requisitos Funcionais (RF)

- **RF01:** Menu principal em modo texto com acesso às funcionalidades do sistema.
- **RF02:** Cadastro, listagem e alteração de itens com código, descrição, tipo (`PA`, `SA`, `MP`), unidade de medida, custo unitário, lead time (semanas), estoque de segurança e lote mínimo.
- **RF03:** Cadastro de estrutura de produto (BOM) em até 3 níveis (`PA -> SA -> MP`) e exibição indentada em árvore.
- **RF04:** Registro de movimentações de estoque (`ENTRADA`, `SAIDA`, `AJUSTE`) com data, quantidade e documento/motivo, atualizando saldo e histórico.
- **RF05:** Consulta de saldo e extrato (Kardex) por item, com alerta quando o saldo fica abaixo do estoque de segurança.
- **RF06:** Cadastro de centros de trabalho (capacidade semanal em horas e custo/hora) e roteiros de operação única para itens fabricados.
- **RF07:** Cadastro e alteração do Plano Mestre de Produção (MPS) para produtos acabados em horizonte de 8 semanas.
- **RF08:** Execução do cálculo MRP para todos os itens, exibindo necessidade bruta, recebimentos programados, estoque projetado, necessidade líquida, recebimentos planejados e liberações planejadas por semana.
- **RF09:** Geração de ordens planejadas (`OP` para itens fabricados e `OC` para matérias-primas) com semanas de liberação e entrega.
- **RF10:** Controle do ciclo de vida das ordens (`PLANEJADA -> FIRME -> LIBERADA -> ENCERRADA`).
- **RF11:** Apontamento de produção de `OP` liberada pela quantidade total, validando e baixando componentes, registrando entrada do item produzido e encerrando a ordem.
- **RF12:** Análise de Carga x Capacidade (CRP) por centro de trabalho e semana, com alerta de sobrecarga.
- **RF13:** Cálculo de custo padrão de itens fabricados somando componentes da BOM e custo de processamento no centro de trabalho.
- **RF14:** Exportação em CSV da posição de estoque e da lista de ordens.
- **RF15:** Persistência automática dos dados na pasta `data/` ao iniciar e encerrar o sistema.
- **RF16:** Geração de gráficos com `matplotlib` (exibidos na tela e salvos em PNG na pasta `data/`): saldo atual x estoque de segurança, estoque projetado em 8 semanas com linha do estoque de segurança, ordens por semana de entrega (barras empilhadas) e carga x capacidade por centro de trabalho.

### Requisitos Não Funcionais (RNF) e Regras de Negócio (RN)

- **RNF01 - RNF09:** Projeto individual em Python 3.10+, estruturado em módulos coesos, com validação de entradas, persistência em JSON/CSV, lógica de negócio implementada sem bibliotecas de ERP/MRP e base de demonstração em `data/` (mínimo de 2 `PA`, 2 `SA`, 8 `MP` e 2 centros de trabalho).
- **RN01 - RN10:** Validação de código `Tipo-Número`, proibição de saldo negativo em saídas/ajustes/apontamentos, restrição de BOM a 3 níveis sem ciclos, processamento hierárquico `PA -> SA -> MP`, fórmulas de necessidade líquida, lote mínimo, lead time com sinalização de ordens `ATRASADA`, recálculo de ordens `PLANEJADA` preservando `FIRME` e `LIBERADA`, cálculo de carga em centros de trabalho e imutabilidade do histórico no Kardex.

## 4. Decisões de Projeto

1. **Modularização por domínio funcional:** Cada responsabilidade (cadastros, BOM, estoque, MPS, MRP, ordens, CRP, custos, relatórios, gráficos e persistência) foi isolada em seu próprio módulo para facilitar manutenção, leitura e apresentação técnica.
2. **Funções utilitárias centralizadas em `utils.py`:** A leitura tipada de inteiros e decimais (com suporte a vírgula e ponto, limites mínimos/máximos e valores padrão), normalização de textos/códigos e a normalização de estruturas da BOM (`iterar_componentes`) foram centralizadas para evitar repetição e reduzir erros de entrada.
3. **Separação entre ordens planejadas e ordens firmes/liberadas:** A cada execução do MRP, apenas ordens com status `PLANEJADA` são substituídas; ordens `FIRME` e `LIBERADA` permanecem íntegras e entram como recebimentos programados (`RP`) no cálculo.
4. **Integridade no apontamento de produção:** Antes de baixar qualquer componente do estoque ou registrar entrada do item produzido, todas as necessidades da BOM são verificadas; se faltar algum componente, o apontamento é rejeitado sem deixar saldos parciais inconsistentes.
5. **Persistência híbrida em JSON e CSV:** Os cadastros e estados do sistema são persistidos em arquivos `.json` em `data/` e o histórico de movimentações (Kardex) em `data/movimentos.csv`, além da exportação de relatórios CSV e gráficos PNG.

## 5. Como Executar em Ambiente Linux (e Windows/Python 3.10+)

### Pré-requisitos

- Python 3.10 ou superior.
- Biblioteca `matplotlib` instalada (para a geração e exibição dos gráficos do RF16).

### Instalação e execução no Linux

```bash
git clone [https://github.com/Vinicius-Vazquez/MRP2_PedalForte.git](https://github.com/Vinicius-Vazquez/MRP2_PedalForte.git)
cd MRP2_PedalForte
python3 --version
pip install matplotlib
python3 main.py
```

Ao encerrar o programa pela opção `0. Sair` (ou ao finalizar o bloco `finally` em `main.py`), os dados modificados são gravados automaticamente na pasta `data/`.

## 6. Fluxo de Uso Recomendado

1. **Cadastros (Opção 1):** Conferir ou cadastrar itens (`PA`, `SA`, `MP`), estrutura de produto (BOM), centros de trabalho e roteiros de produção.
2. **Estoque e Kardex (Opção 2):** Registrar entradas, saídas ou ajustes e consultar saldos e alertas de estoque de segurança.
3. **MPS (Opção 3):** Definir ou ajustar a demanda semanal (semanas 1 a 8) dos produtos acabados.
4. **Executar MRP (Opção 4):** Calcular necessidades brutas, recebimentos programados, estoque projetado, necessidades líquidas, recebimentos planejados e liberações planejadas.
5. **Ordens (Opção 5):** Gerar `OP` e `OC` a partir do MRP, alterar status (`PLANEJADA -> FIRME -> LIBERADA`) e realizar o apontamento de produção de `OP` liberada.
6. **CRP e Custos (Opções 6 e 7):** Verificar carga versus capacidade dos centros de trabalho e calcular/atualizar o custo padrão dos itens.
7. **Relatórios e Gráficos (Opções 8 e 9):** Exportar os relatórios CSV e gerar os gráficos de acompanhamento em PNG na pasta `data/`.

## 7. Autor

- **Vinícius Souza Vazquez** — Engenharia da Computação, CEFET-MG Campus Divinópolis.