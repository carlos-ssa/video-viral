# Itens 3D gratuitos: pesquisa, licença e importação

Leia ao precisar de objetos, personagens, cenários, materiais ou HDRIs para o [fluxo 3D](modules/3d.md). Antes de modelar, busque um item existente compatível com a função no plano e com o pack de referências visuais. Biblioteca de conteúdo não acrescenta um motor ao [stack](../assets/stack.json); use Blender, Three.js e glTF Transform já previstos, conforme necessidade e disponibilidade.

## Buscar e escolher

1. Descreva o necessário: objeto, época, proporções, realismo/estilização, paleta, superfície, distância da câmera e animação/rig. Pesquise termos em português e inglês, por exemplo `wooden chair low poly CC0` ou `industrial lamp PBR glTF`. Use páginas oficiais e filtros de gratuidade, licença e formato; anúncio de resultado não confirma download disponível.
2. Compare poucos candidatos com os quadros de referência: silhueta, escala, detalhe, desgaste, materiais e linguagem visual. Um modelo fotogramétrico pode destoar de uma peça estilizada. Escolha adaptar, modelar ou usar proxy quando nenhum candidato servir; registre o motivo. Gratuito não exige aceitar incompatibilidade estética.
3. Antes do download, confirme página do item/pacote, autor, licença aplicável à versão e uso pretendido. Gratuito significa preço; não garante uso comercial, adaptação ou redistribuição. Não trate catálogo, render de exemplo ou licença do site como licença comprovada de um arquivo específico. Marcas, pessoas e propriedades representadas podem exigir direitos adicionais.

### Fontes iniciais verificadas em 13/11/2026

| Fonte e busca | Adequação | Licença e limite observado |
|---|---|---|
| [Poly Haven: modelos](https://polyhaven.com/models) | Objetos realistas; também oferece materiais e HDRIs | [Ativos CC0](https://polyhaven.com/license), uso comercial sem atribuição obrigatória. Render promocional e conteúdo do site têm termos distintos. Exemplo de item consultado: [Wooden Chair 01, Jake Mobley](https://polyhaven.com/a/WoodenChair_01), com CC0 e opções de resolução/formato na página; não foi baixado/testado. |
| [Kenney: Furniture Kit](https://kenney.nl/assets/furniture-kit) | Mobiliário de linguagem simples para cenas estilizadas | Página oficial indexada identifica pacote 3D e CC0; [suporte](https://kenney.nl/support) explica CC0 dos assets. Abertura direta indisponível nesta consulta; confirmar página/arquivo de licença ao obter o pacote. O pacote é exemplo específico, não confirmação de todos os produtos do autor. |
| [Quaternius](https://quaternius.com/) | Packs de personagens, animações e objetos estilizados | [QAL v1.0](https://quaternius.com/license.html), atualizada em 28/08/2026: produtos comerciais e modificações permitidos; redistribuir os arquivos como assets é proibido. A [FAQ](https://quaternius.com/faq.html) ainda diz CC0: há divergência. Confira licença do pacote/versão e preserve evidência; não atribua CC0 por hábito nem decida uma dúvida jurídica por inferência. |
| [Blendkit, antigo BlenderKit: licenças](https://www.blendkit.com/docs/licenses/) | Catálogo variado; buscar itens marcados gratuitos | A documentação distingue CC0 de Royalty Free; permite uso comercial, mas Royalty Free restringe revenda do ativo. Confirme preço/acesso e licença do item. Não instalar addon ou MCP apenas para pesquisar nem presumir que todo o catálogo é gratuito. |
| [Sketchfab: filtros de licença](https://www.sketchfab.com/blogs/community/refine-downloadable-model-searches-with-new-license-filters/) | Variedade de objetos e digitalizações | Fonte oficial indexada explica filtros e restrições NC; abertura direta retornou 403 nesta consulta. Filtre download autorizado e licença por modelo. CC BY exige crédito; NC não libera uso comercial; SA/ND exigem análise dos termos para a adaptação/entrega pretendida. Conta, disponibilidade e condições atuais precisam ser conferidas no item. |

As linhas são pontos de partida de pesquisa, não uma lista de arquivos aprovados para produção. Não assumir formato, peso, rig ou licença de um item ainda não examinado. Sem acesso, registrar a limitação e escolher outra fonte ou pedir somente a informação essencial.

## Obter e conferir sem alterar a sessão do usuário

- Baixe apenas arquivos necessários por links oficiais autorizados. Não contorne login, pagamento, CAPTCHA ou restrição de acesso; não extraia geometria de um viewer sem permissão. Use integração já disponível quando apropriada, sem instalar addon/MCP por conveniência. Registre acesso pendente se depender de credencial ausente.
- Antes de transferir, confira formato suportado pela versão instalada, tamanho do arquivo/pacote, triângulos quando informados, mapas e resolução de textura. Prefira GLB/glTF para transporte PBR/Three.js; FBX conforme suporte para rig/animação; OBJ para geometria estática com materiais limitados. A extensão não garante fidelidade.
- No perfil de GPU de 8 GB, comece com variante leve/LOD e texturas 1K–2K adequadas ao tamanho em tela; evite scans densos, subdivisão pesada e pacotes inteiros sem necessidade. Peso em disco não mede VRAM: conte também texturas descomprimidas, geometria, luzes e custo do render. Faça teste pequeno antes de escalar; não fixe um orçamento universal sem medir a cena.
- Importe primeiro em cena/arquivo de teste separado, preservando fonte e projeto atual. Não abra um `.blend` externo por cima da sessão gráfica do usuário. Se `.blend` for indispensável, use processo separado com autoexec desativado (`--disable-autoexec`/`-Y` antes do arquivo), sem marcar fonte como confiável nem autorizar scripts. Isso reduz execução automática; não é um sandbox. [Manual oficial de segurança](https://docs.blender.org/manual/en/3.6/advanced/scripting/security.html).
- Confira geometria/normais, UVs, mapas e caminhos de texturas, cores/PBR/normal maps, materiais transparentes, pivô/origem, unidades, escala física, orientação/eixos e transformações. Para rig, verifique pose, deformação, nomes, duração/FPS e loop; valide LOD no enquadramento real. Exporte e reimporte um trecho quando houver conversão. Não declare fidelidade ou adaptação concluída sem inspeção do resultado.
- Ajuste só o necessário à direção: escala, paleta, materiais, simplificação e variações. Salve versão derivada e anote mudanças realmente realizadas, ferramenta e resultado do teste; conserve licença e autoria do original. Importação bem-sucedida não prova adequação visual.

## Registro e portão de entrega

Mantenha candidatos e referências apenas de análise em `research/`/`research.sources`, conforme [pesquisa](research.md). Fotos, vídeos e previews estudados não entram como ativos usados só por terem orientado uma escolha; uso efetivo em cena/composição exige origem e licença próprias.

Para cada arquivo efetivamente usado, registre em `assets[]` os campos existentes `path`, `kind:"model"`, `source`, `license`, `commercial_ok`; `role` é opcional para descrever a função. Texturas/HDRIs externos usados também precisam de registro com tipo coerente. O registro não substitui a evidência: mantenha em ficha de proveniência em `research/` URL exata do item e licença, autor, data de coleta/download, versão, atribuição exigida e onde foi aplicada, formato, tamanho, texturas, escala e alterações/testes. Preserve o texto/arquivo de licença obtido junto do ativo e identifique a ficha em `source`.

Exemplo ilustrativo para preencher **somente depois** de usar e verificar esse arquivo; o guia não o baixou nem produziu:

```json
{
  "path": "assets/3d/cadeira/scene.gltf",
  "kind": "model",
  "role": "cenario",
  "source": "Jake Mobley / Poly Haven; https://polyhaven.com/a/WoodenChair_01; evidencia: research/assets/cadeira.md",
  "license": "CC0 1.0; https://polyhaven.com/license",
  "commercial_ok": true
}
```

Defina `commercial_ok:true` somente com permissão confirmada para o uso pretendido. Licença ausente, conflitante ou não verificada continua pendente (`commercial_ok:false` e descrição fiel); substitua o ativo ou resolva a evidência. `deliver.py` verifica os registros e bloqueia licença pendente/incompatível; passar o portão técnico não comprova análise jurídica, autoria ou qualidade visual. Não apagar ativos realmente usados nem renomear uma licença para passar o portão. `--draft` identifica rascunho conforme o fluxo existente, sem liberar publicação.
