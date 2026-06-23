
# Regras Aprendidas do PartiuViajar

## 1. Modificações em Arquivos Estáticos com Docker
Sempre que fizer alterações no frontend (HTML, CSS, JS) ou arquivos estáticos, **verifique obrigatoriamente** o arquivo docker-compose.yml. Se a pasta static/ não estiver montada como um volume (ex: - ./static:/app/static), o contêiner continuará servindo a versão antiga dos arquivos gravada durante o docker build.
Solução: Adicione o volume no docker-compose.yml ou use docker cp para enviar os arquivos diretamente para o contêiner em execução.

## 2. Concorrência com SQLAlchemy Async e Worker Threads (Dramatiq)
Quando trabalhar com Dramatiq (ou outro worker síncrono que cria threads) e precisar usar SQLAlchemy Async (syncpg), **nunca utilize uma instância global** de create_async_engine ou AsyncSessionLocal através de syncio.run(). Compartilhar a mesma engine async entre loops de eventos diferentes causa o erro InterfaceError: cannot perform operation: another operation is in progress.
Solução: Crie instâncias locais isoladas do engine e da session dentro de cada tarefa assíncrona, e não se esqueça de rodar wait engine.dispose() no bloco inally.
