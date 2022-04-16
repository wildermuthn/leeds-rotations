import { gql } from "@apollo/client"


export const MAKE_PREDICTIONS = gql`
  mutation MakePredictions($ids: [ID!]!) {
    makePredictions(ids: $ids) {
      errors
    }
  }
`

export const SELECTED_FACES = gql`
  query Root {
    session
    selectedFaces {
      id
      url
      filePath
      prediction
    }
  }
`


export const LATEST_FACES = gql`
  query Root {
    session
    latestFaces {
      id
      url
      filePath
      prediction
    }
  }
`

export const GENERATE_RANDOM_FACES = gql`
  mutation GenerateRandomFaces($input: generateRandomFacesInput!) {
    generateRandomFaces(input: $input) {
      faces {
        id
        url
        filePath
        prediction
      }
      errors
    }
  }
`

export const GENERATE_PREDICTED_FACES = gql`
  mutation GeneratePredictedFaces($matchThreshold: Float!) {
    generatePredictedFaces(matchThreshold: $matchThreshold) {
      faces {
        id
        url
        filePath
        prediction
      }
      errors
    }
  }
`

export const GENERATE_VARIANT_FACES = gql`
  mutation GenerateVariantFaces($id: ID!, $similarity: Int) {
    generateVariantFaces(id: $id, similarity: $similarity) {
      errors
    }
  }
`
export const GENERATE_SORTED_FACES = gql`
  mutation GenerateSortedFaces($id: ID) {
    generateSortedFaces(id: $id) {
      errors
    }
  }
`

export const GENERATE_AVERAGED_FACES = gql`
  mutation GenerateAveragedFaces {
    generateAveragedFaces {
      faces {
        id
        url
        filePath
        prediction
      }
      errors
    }
  }
`

export const RESET_SESSION = gql`
  mutation ResetSelections($input: resetSelectionsInput!) {
    resetSelections(input: $input) {
      errors
    }
  }
`

export const REMOVE_LATEST_FACES = gql`
  mutation RemoveLatestFaces {
    removeLatestFaces {
      errors
    }
  }
`

export const ADD_FACE_MATCHES = gql`
  mutation TrainFaceMatches($input: trainFaceMatchesInput!) {
    trainFaceMatches(input: $input) {
      faces {
        id
        url
        filePath
        prediction
      }
      errors
    }
  }
`

export const TRAIN_SORTED_FACES = gql`
  mutation TrainSortedFaces {
    trainSortedFaces {
      errors
    }
  }
`

export const ADD_SORTED_FACES = gql`
  mutation AddSortedFaces($input: sortedFaces!) {
    addSortedFaces(input: $input) {
      errors
    }
  }
`
