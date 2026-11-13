# Pesquisa de nicho, plataforma e Google Trends

A pesquisa orienta decisões criativas. Ela não revela pesos internos dos algoritmos nem comprova que um vídeo será viral.

## Recorte e evidências

Defina nicho, idioma/região, plataforma, formato/duração, objetivo e período. Busque referências recentes e recorrentes, não apenas o maior vídeo isolado. Use a busca web disponível e informações públicas realmente acessíveis. Metadados/legendas fornecidos podem apoiar a pesquisa, sem instalar um downloader adicional. Estudar não autoriza reaproveitar ativos.

Compare referências com contexto: tamanho e histórico da conta quando públicos, idade da publicação, série/formato e distribuição paga quando identificável. Visualizações/dia é só um sinal auxiliar. Registre abertura visual/verbal, promessa, organização, ritmo, enquadramento, performance, payoff e CTA. Para avaliar montagem real, inspecione a mídia com uma ferramenta disponível; metadados e legendas não revelam transições ou linguagem de câmera.

Em `research.sources`, mantenha URL, data de coleta, filtros/recorte, observação e tipo:

- `public_observation`: métrica ou padrão público realmente observado.
- `owned_analytics`: dado fornecido/autorizado do próprio canal, com intervalo e definição.
- `hypothesis`: inferência que será testada; não apresentar como fato do algoritmo.

## Ficha de referência por plano

Método inspirado no [rea-video](https://github.com/JuneYaooo/rea-video), projeto Apache-2.0: adotar somente a ideia de leitura em camadas e evidências por plano, sem copiar código, instalar ou integrar o projeto. A licença do método/ferramenta não licencia os vídeos estudados; estudar referência não autoriza reutilização.

Organize as notas em `research/` para ler só o necessário:

1. **Cartão do vídeo:** URL, fonte/data, contexto, duração conhecida, promessa e limites de acesso. Diga se houve reprodução integral, parcial ou apenas consulta a relato/metadados.
2. **Linha do tempo:** uma linha por plano, com intervalo, ação e grupo de cenário/identidade; serve de mapa para o detalhe.
3. **Detalhe por cena/plano:** preencher a ficha abaixo. Agrupar tomadas do mesmo cenário e da mesma identidade ajuda a estudar continuidade e planejar produção em lotes, sem confundir tomadas distintas.

| Campo | Registro |
|---|---|
| Plano / cena / grupo | ID do plano, cena e grupo de cenário/identidade; indicar identidade incerta |
| Tempo | Início–fim observado na mídia; sem acesso, registrar indisponível, nunca inventar timecode |
| Observado | O que efetivamente se vê/ouve, separado de explicações sobre como foi feito |
| Inferido | Hipótese de técnica, intenção ou origem (filmado/IA/3D); classificação é estimativa, não detecção comprovada |
| Evidência | URL e trecho, quadro/timecode ou citação da fonte; distinguir inspeção direta de relato de terceiros |
| Confiança | Alta/média/baixa, com motivo e lacunas; não usar uma nota como prova de origem |

Sem assistir, registre apenas o que a fonte relata e deixe montagem/câmera/som como não verificados. Os exemplos do [catálogo de virais com IA](formats/virais-ia.md#fotografia-da-pesquisa-13112026) são pesquisa documental não assistida, não fichas de inspeção audiovisual.

## Google Trends

Use para interesse de busca, sazonalidade, termos relacionados e escolha do ângulo. Compare termos ou tópicos com a mesma região, período, categoria e propriedade. Use Pesquisa do YouTube para interesse de busca no YouTube; isso não mede a recomendação no feed de Shorts. Pesquisa Web pode revelar demanda por produtos e serviços, mas não mede demanda de compra diretamente.

1. Gere o link: `python scripts/trends.py <projeto> --terms "barbearia" "salao de beleza" --geo BR --timeframe "today 3-m" --property youtube`.
Use `--category <ID>` quando houver uma categoria escolhida no Trends (0 mantém todas).
2. Abra a URL com o navegador disponível e confira os filtros. Use também um período maior para distinguir pico isolado de sazonalidade. Guarde a consulta e as observações; sem acesso à página, registre a limitação e avance com outras evidências.
3. No gráfico **Interesse ao longo do tempo**, exporte o CSV oficial. Importe com o mesmo comando e `--csv <arquivo>`. Use `--terms` na ordem e com os nomes das séries da exportação. O importador não baixa dados, não interpreta CSV de regiões e não confirma automaticamente os filtros escolhidos no navegador.
4. O script preserva o CSV e seu SHA-256 em `research/trends/`, grava a série e a proveniência em JSON e referencia o registro em `video.json`. Não reexecute se os dados/filtros não mudaram.

Os índices do site são relativos (0–100), não volume absoluto. Zero também pode representar dados insuficientes; `<1` permanece censurado, sem ser convertido para zero. Não junte índices de exportações independentes como se tivessem a mesma escala. Dados recentes podem estar incompletos; registre isso na análise. `filters_provenance` informa que período/região são declarados na importação, exigindo conferência com a exportação.

A [API oficial](https://developers.google.com/search/apis/trends) está documentada como alpha com acesso limitado: use somente se o usuário já tiver acesso e um conector válido. O importador desta skill cobre o CSV do site, não a escala da API. Não instalar pytrends nem depender de endpoints internos como integração garantida. Na ausência de API, navegador + exportação oficial é o caminho documentado.

Fontes oficiais: [normalização e amostragem](https://support.google.com/trends/answer/4365533), [exportação e atribuição](https://support.google.com/trends/answer/4365538). Cite Google Trends ao reutilizar os dados. As condições atuais de acesso podem mudar.

## Transformar pesquisa em decisões

Em `research.hypotheses`, ligar observação → interpretação → decisão de gancho/roteiro/visual → métrica futura. Exemplo hipotético: interesse recorrente em um problema de estoque → demonstrar esse problema no quadro inicial → verificar atenção e pedidos de demonstração após publicar. Não inventar os resultados.

Se houver analytics reais: localizar quedas, distinguir perda no gancho de abandono antes da prova/CTA e preparar uma mudança por vez. Não fixar metas universais de retenção para durações, nichos e plataformas diferentes. Sem analytics, a entrega é uma hipótese criativa bem produzida, não uma previsão comprovada.
