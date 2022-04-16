import React from 'react'
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'
import { ApolloProvider } from '@apollo/client/react'

function uuidv4 () {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    // eslint-disable-next-line
    const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16)
  })
}

const httpLink = createHttpLink({
  uri: 'http://34.135.223.27:4000/graphql'
})

const sessionLink = setContext((_, { headers }) => {
  const storage = window.sessionStorage
  let session = sessionStorage.getItem('session')
  if (!session) {
    session = uuidv4()
    storage.setItem('session', session)
  }
  return {
    headers: {
      ...headers,
      session
    }
  }
})

const client = new ApolloClient({
  link: sessionLink.concat(httpLink),
  cache: new InMemoryCache()
})

const Apollo = ({ children }) => {
  return (
    <ApolloProvider client={client}>
      {children}
    </ApolloProvider>
  )
}

export default Apollo
