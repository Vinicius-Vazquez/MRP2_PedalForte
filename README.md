```markdown
# MRP II - Pedal Forte Bicicletas

Sistema de Planejamento dos Recursos de Manufatura (MRP II) desenvolvido em Python para a fábrica fictícia **Pedal Forte Bicicletas Ltda.** (Divinópolis - MG), no contexto da disciplina de Programação em Python do curso de Engenharia de Computação do CEFET-MG (Campus Divinópolis)[cite: 2, 3].

## Visão Geral

O sistema substitui o controle fragmentado em planilhas por uma solução modular em modo texto, integrando cadastro de itens, estrutura de produto (BOM) em até três níveis, gestão de estoques e kardex, Plano Mestre de Produção (MPS), cálculo MRP em horizonte de 8 semanas, ciclo de ordens de produção (OP) e compra (OC), apontamento de produção, análise de carga versus capacidade (CRP), cálculo de custo padrão, exportação em CSV, geração de gráficos com `matplotlib` e persistência automática de dados[cite: 3, 4, 5, 13].

## Arquitetura do Projeto

O código segue uma organização modular orientada a responsabilidades específicas[cite: 5]:

```text
MRP2_PedalForte/
├── main.py            # Ponto de entrada, inicialização e encerramento com persistência
├── menu.py            # Menu principal e navegação entre módulos
├── itens.py           # Cadastro, listagem e alteração de itens (PA, SA, MP)
├── estrutura.py       # Cadastro da BOM (até 3 níveis) e explosão indentada
├── estoque.py         # Movimentações, consulta de saldo, alertas e kardex
├── mps.py             # Cadastro e alteração do Plano Mestre de Produção (8 semanas)
├── mrp.py             # Cálculo MRP, necessidade líquida, lote mínimo e lead time offset
├── ordens.py          # Geração de OPs/OCs, transição de status e apontamento de produção
├── capacidade.py      # Centros de trabalho, roteiros de operação e análise CRP
├── custos.py          # Cálculo do custo padrão (materiais + mão de obra) via BOM
├── relatorios.py      # Exportação de relatórios CSV (estoque e ordens)
├── graficos.py        # Geração e exibição de gráficos gerenciais (matplotlib)
├── persistencia.py    # Leitura e gravação de dados na pasta data/
├── utils.py           # Funções auxiliares e validações
└── data/              # Base de demonstração (JSON/CSV) e artefatos gerados (CSV/PNG)

```

## Decisões de Projeto

* **Separação por domínio funcional:** Cada regra do MRP II (itens, estrutura, estoque, MPS, MRP, ordens, capacidade, custos, relatórios e gráficos) reside em módulo próprio, facilitando manutenção, leitura e explicação técnica.


* **Lógica de negócio própria em Python puro:** Os cálculos de explosão de necessidades, estoque projetado, necessidade líquida, lote mínimo, lead time offset, carga de centro de trabalho e custo padrão foram implementados diretamente no código, sem uso de bibliotecas prontas de ERP/MRP.


* **Dicionário central em memória com persistência em arquivos:** `main.py` carrega os dados da pasta `data/` ao iniciar e salva automaticamente ao encerrar, mantendo os arquivos JSON/CSV sincronizados com o estado da aplicação.


* **Hierarquia rigorosa da BOM e do MRP:** A estrutura respeita até três níveis (`PA -> SA -> MP`), impedindo ciclos e tratando matérias-primas (`MP`) como itens comprados sem estrutura. O cálculo MRP processa os itens na sequência `PA -> SA -> MP`.


* **Controle de ciclo de vida das ordens e integridade de saldo:** Apenas ordens `FIRME` ou `LIBERADA` entram como recebimentos programados, enquanto ordens `PLANEJADA` são recalculadas a cada execução do MRP. Movimentações de estoque e apontamentos de OPs liberadas validam disponibilidade de saldo antes de aplicar alterações e registram histórico sem exclusão destrutiva.


* **Visualização dupla nos gráficos:** Os gráficos gerados com `matplotlib` são salvos em PNG na pasta `data/` e exibidos em janela interativa na tela.



## Requisitos e Ambiente

* **Linguagem:** Python 3.10 ou superior.


* **Sistema operacional:** Compatível com execução em Linux e ambientes desktop Python.


* **Dependência gráfica:** `matplotlib` (para geração dos gráficos de gestão).



## Instruções de Execução

1. Clone o repositório e acesse a pasta do projeto:

```bash
git clone [https://github.com/Vinicius-Vazquez/MRP2_PedalForte.git](https://github.com/Vinicius-Vazquez/MRP2_PedalForte.git)
cd MRP2_PedalForte

```

2. Certifique-se de que o `matplotlib` está instalado no ambiente Python 3.10+:



```bash
python3 -m pip install matplotlib

```

3. Execute o ponto de entrada do sistema:

```bash
python3 main.py

```

(Em ambientes Windows onde o comando padrão é `python`, utilize `python main.py` dentro do diretório do projeto.)

## Instruções de Uso

Ao iniciar o sistema, o menu principal apresenta as seguintes opções:

1. **Cadastros (itens, estrutura, centros, roteiros):** Cadastre, liste e altere itens (`PA`, `SA`, `MP`) com código no padrão `Tipo-Número`, unidade, custo unitário, lead time, estoque de segurança e lote mínimo; configure a BOM em até 3 níveis e visualize a árvore indentada; cadastre centros de trabalho (horas/semana e custo-hora) e roteiros (centro e tempo unitário).


2. **Estoque (movimentar, saldo, kardex):** Registre entradas, saídas e ajustes com data, quantidade e documento/motivo (bloqueando saídas que deixem o saldo negativo); consulte saldos com alerta abaixo do estoque de segurança e visualize o kardex.


3. **Plano Mestre de Produção (MPS):** Cadastre e altere a demanda semanal dos produtos acabados ao longo do horizonte de 8 semanas.


4. **Executar MRP:** Calcula necessidade bruta, recebimentos programados, estoque projetado, necessidade líquida, recebimentos planejados e liberações planejadas na ordem `PA -> SA -> MP`, sinalizando liberações anteriores à semana 1 como `ATRASADA`.


5. **Ordens de produção e de compra:** Gere OPs e OCs a partir das liberações planejadas, liste ordens, altere status (`PLANEJADA -> FIRME -> LIBERADA -> ENCERRADA`) e realize o apontamento de produção de OPs liberadas (verificando e baixando componentes, dando entrada no item produzido e encerrando a ordem).


6. **Carga x capacidade (CRP):** Exibe carga em horas, percentual de utilização e sinalização de sobrecarga por semana para cada centro de trabalho com base nas OPs liberadas.


7. **Custo padrão dos produtos:** Calcula e exibe o custo padrão de itens fabricados somando componentes da estrutura e mão de obra do roteiro.


8. **Relatórios (exportar CSV) e Gráficos:** Exporte a posição de estoque e a lista de ordens para arquivos CSV em `data/`, e gere os gráficos de estoque x estoque de segurança, estoque projetado nas 8 semanas, ordens (OP/OC) por semana de entrega e carga x capacidade por centro.



## Mapeamento dos Requisitos Funcionais

* **RF01:** Menu principal do sistema (`menu.py`).


* **RF02:** Cadastro, listagem e alteração de itens (`itens.py`).


* **RF03:** Cadastro e explosão indentada da BOM em até 3 níveis (`estrutura.py`).


* **RF04:** Registro de movimentações de estoque com atualização de saldo (`estoque.py`).


* **RF05:** Consulta de saldo, alerta de estoque de segurança e kardex (`estoque.py`).


* **RF06:** Cadastro de centros de trabalho e roteiros de operação (`capacidade.py`).


* **RF07:** Cadastro e alteração do MPS para 8 semanas (`mps.py`).


* **RF08:** Execução do cálculo MRP e exibição dos registros semanais por item (`mrp.py`).


* **RF09:** Geração de ordens planejadas de produção (OP) e compra (OC) (`ordens.py`).


* **RF10:** Controle de status das ordens (`PLANEJADA`, `FIRME`, `LIBERADA`, `ENCERRADA`) (`ordens.py`).


* **RF11:** Apontamento de produção de OP liberada com baixa de componentes e encerramento (`ordens.py`).


* **RF12:** Análise de carga x capacidade (CRP) com identificação de sobrecarga (`capacidade.py`).


* **RF13:** Cálculo do custo padrão percorrendo a estrutura de produto e roteiro (`custos.py`).


* **RF14:** Exportação CSV da posição de estoque e da lista de ordens (`relatorios.py`).


* **RF15:** Persistência automática em arquivos na pasta `data/` (`persistencia.py`, `main.py`).


* **RF16:** Geração de gráficos gerenciais com `matplotlib` exibidos em tela e salvos em PNG (`graficos.py`).



## Autoria e Contexto Acadêmico

Projeto individual desenvolvido por **Vinicius Vazquez** no curso de Engenharia de Computação da **UFCI-MG (Campus Divinópolis)**, para a disciplina de Programação em Python (Prof. Guido Pantuza), referente ao 2º Trabalho: Sistema MRP II Pedal Forte.

```

```
