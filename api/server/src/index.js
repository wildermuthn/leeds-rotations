const path = require('path')
const express = require('express')
const _ = require('lodash')
const { ApolloServer, gql } = require('apollo-server-express')
const process = require('process')
const { typeDefs } = require("./typedefs.js")
const { resolvers } = require("./resolvers.js")

process.on('SIGINT', () => {
  console.info("Interrupted")
  process.exit(0)
})


async function startApolloServer() {

  const server = new ApolloServer({
    typeDefs,
    resolvers,
    playground: {
      settings: {
        'editor.theme': 'light',
      },
    },
    context: (context) => {
      const sessionId = _.get(context, 'req.headers.session')
      return { sessionId }
    }
  });
  await server.start();

  const app = express();
  // app.use(express.static(path.join(__dirname, '../../../experiments')));
  server.applyMiddleware({
    app,
    cors: {
      origin: '*',
      credentials: true
    }});

  await new Promise(resolve => app.listen({ port: 4000 }, resolve));
  console.log(`🚀 Server ready at http://localhost:4000${server.graphqlPath}`);
  return { server, app };
}

startApolloServer()
