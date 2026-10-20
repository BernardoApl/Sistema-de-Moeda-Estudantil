# Ferramentas opcionais

Não são necessárias para iniciar o sistema. Execute a partir da raiz do repositório.

- `preparar_entregas.py`: regenera fontes dos diagramas, apresentação HTML e snapshot da sprint 2 a partir da versão final. **Sobrescreve esses artefatos gerados**; preserve edições manuais antes de executar. Não altera bancos.
- `verificar_interface.py`: QA com Playwright e Chrome instalado; usa banco temporário e cria capturas em `tmp/qa`. Instale `playwright` e Flask no ambiente do script.

```powershell
python ferramentas/preparar_entregas.py
python ferramentas/verificar_interface.py
```

Para renderizar UML, use Java e o JAR oficial do PlantUML, disponível em https://github.com/plantuml/plantuml/releases. Os diagramas usam Smetana e dispensam Graphviz.

```powershell
java -jar caminho/plantuml.jar -charset UTF-8 -tsvg "Entrega Sprint 1/diagramas/*.puml" "Entrega Sprint 2/diagramas/*.puml"
java -jar caminho/plantuml.jar -charset UTF-8 -tpng "Entrega Sprint 1/diagramas/*.puml" "Entrega Sprint 2/diagramas/*.puml"
```
