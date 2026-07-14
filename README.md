# 🛒 Lojinha da Unidade

Projeto desenvolvido durante o curso de **Análise e Desenvolvimento de Sistemas (ADS)** com o objetivo de colocar em prática os conhecimentos de HTML, CSS e JavaScript que fui adquirindo ao longo da faculdade.

---

## 💡 De onde surgiu a ideia?

A ideia foi simples: criar algo que eu pudesse ver funcionando de verdade, não só exercícios soltos. Decidi fazer um mini e-commerce onde o usuário consegue escolher produtos, controlar a quantidade e ver o valor total sendo atualizado na hora. Nada muito complexo, mas o suficiente para entender como o JavaScript interage com o HTML de forma dinâmica.

---

## O que o projeto faz?

É uma página de loja com uma tabela de produtos. Cada produto tem uma imagem, nome, código, cor e preço. O usuário consegue clicar nos botões de **+** e **-** para adicionar ou remover itens do carrinho, e o total de cada produto e o subtotal geral são calculados automaticamente sem precisar recarregar a página.

Tem também uma validação simples: se você tentar diminuir a quantidade abaixo de zero, aparece um alerta avisando que não é possível.

Os produtos cadastrados são:

| Produto | Preço |
|--------|-------|
| iPhone 15 | R$ 2.000 |
| Asus Go 15 | R$ 3.000 |
| Smartwatch | R$ 800 |
| QCY T24 (fone) | R$ 300 |

---

## 🛠️ Tecnologias que usei

- **HTML5** para a estrutura da página
- **CSS3** para os estilos
- **JavaScript puro** para toda a lógica do carrinho
- **Bootstrap 5.3** para facilitar o layout e deixar a tabela mais apresentável
- **Bootstrap Icons** para os ícones de + e -

---

## 📁 Estrutura de pastas

```
lojinha-da-unidade/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── script.js
└── img/
    ├── carrinho-logo.png
    ├── logo-loja.png
    ├── smartphone.jpeg
    ├── notebook.jpeg
    ├── relogio.jpeg
    └── fone.jpeg
```

---

## ▶️ Como rodar o projeto

Não precisa instalar nada. Só clonar e abrir o arquivo no navegador:

```bash
git clone https://github.com/seu-usuario/lojinha-da-unidade.git
cd lojinha-da-unidade
```

Depois é só abrir o `index.html` no navegador. Se estiver no VS Code, recomendo usar a extensão **Live Server** para ver as alterações em tempo real.

---

## 🌐 Acesse online

O projeto está publicado pelo GitHub Pages:

🔗 **[https://seu-usuario.github.io/lojinha-da-unidade](https://seu-usuario.github.io/lojinha-da-unidade)**

---

## 👨‍💻 Autor

Feito por **[Seu Nome](https://github.com/seu-usuario)** — estudante de ADS
