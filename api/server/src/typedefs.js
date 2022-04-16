const { gql } = require('apollo-server-express')

const typeDefs = gql`
  scalar Date
  scalar JSON
  scalar DateTime
  
  type Query {
    game: JSON
  }
  
`

module.exports = {
  typeDefs,
}
