
const resolvers = {
  Query: {
    session: async (parent, args, { sessionId }) => {
      return sessionId || "No session"
    },
    game: async (parent, args, { sessionId }) => {
      return {"foo": "bar"}
    },
  },
}

module.exports = {
  resolvers,
}
