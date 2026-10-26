# MRP II - Pedal Forte Bicicletas


https://mrp2pedalforte-alzjshfpjt6cbgg7khnuvp.streamlit.app/

Sistema de Informação de Planejamento dos Recursos de Manufatura (MRP II) desenvolvido em Python para a fábrica fictícia Pedal Forte Bicicletas Ltda., no âmbito da disciplina de Programação em Python do CEFET-MG (Campus Divinópolis).

## Aluno / Desenvolvedor
* **Desenvolvedor:** Vinicius Vazquez (Engenharia de Computação)
* **Professor / Product Owner:** Guido Pantuza

---

## 🛠️ Stack Tecnológica
* **Linguagem:** Python 3.10+
* **Biblioteca Gráfica/Relatórios:** Matplotlib (para gráficos de gestão)
* **Persistência de Dados:** Arquivos JSON e CSV na pasta `data/`

---

## 📁 Estrutura do Projeto
```text
MRP2_PedalForte/
│
├── data/                  # Base de dados (JSON e CSV)
├── docs/                  # Documentação e mídias
├── main.py                # Ponto de entrada do sistema
├── menu.py                # Menus e navegação interativa
├── itens.py               # Cadastro e gestão de itens (PA, SA, MP)
├── estrutura.py           # Estrutura de produto (BOM) e árvore indentada
├── estoque.py             # Movimentações, saldo atual e kardex
├── mps.py                 # Plano Mestre de Produção (8 semanas)
├── mrp.py                 # Motor de cálculo MRP
├── ordens.py              # Ordens de Produção (OP), Compra (OC) e Apontamento
├── capacidade.py          # Centros de trabalho, roteiros e CRP (Carga x Capacidade)
├── custos.py              # Cálculo de custo padrão (materiais + mão de obra)
├── relatorios.py          # Exportação de relatórios em CSV
├── graficos.py            # Gráficos de gestão com Matplotlib
├── persistencia.py        # Camada de persistência e base de demonstração
├── utils.py               # Funções utilitárias e validações
└── README.md              # Documentação do projeto
```

## 🚀 Instruções de Execução
1- Certifique-se de ter o Python 3.10+ instalado em seu ambiente.
2- Instale as dependências necessárias (como o Matplotlib):
```text
py -m pip install matplotlib
```
3- Execute o programa principal a partir da raiz do repositório:
```text
py main.py
```

## 📋 Requisitos Implementados (RF e RNF)

RF01 a RF03: Menus interativos, cadastros de itens (PA, SA, MP) e estrutura de produto (BOM) em até 3 níveis com explosão indentada.

RF04 e RF05: Registo de movimentações de estoque (entradas, saídas e ajustes) com validação de saldo negativo e consulta ao Kardex.

RF06 e RF07: Gestão de Centros de Trabalho, Roteiros de Operação e Plano Mestre de Produção (MPS) para horizonte de 8 semanas.

RF08 a RF11: Cálculo completo do MRP, geração de ordens planejadas (OP/OC), gestão de estados (Firme, Liberada, Encerrada) e apontamento de produção com baixa automática no stock.

RF12 a RF14: Análise de Carga x Capacidade (CRP) com alerta de sobrecarga, cálculo de custo padrão e exportação de relatórios em formato CSV.

RF15 e RF16: Persistência automática em JSON/CSV na pasta data/ e geração de gráficos de gestão com Matplotlib.
