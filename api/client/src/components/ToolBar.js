import React, { useCallback, useState } from 'react'
import _ from 'lodash'
import {
  ButtonGroup as _ButtonGroup,
  Button,
} from '@material-ui/core'
import styled from 'styled-components/macro'
import MatchThreshold from "./MatchThreshold"
import { useMutation } from "@apollo/client"
import {
  GENERATE_RANDOM_FACES,
  GENERATE_PREDICTED_FACES,
  GENERATE_VARIANT_FACES,
  ADD_FACE_MATCHES,
  RESET_SESSION,
  REMOVE_LATEST_FACES,
  LATEST_FACES,
  SELECTED_FACES,
  ADD_SORTED_FACES,
  TRAIN_SORTED_FACES,
  GENERATE_SORTED_FACES,
} from "../queries"

const ShortWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-around;
  position: absolute;
  height: 0px;
  top: 77px; left:0; right:0;
  padding: 0;
  margin: 0 20px;
`

const Wrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-around;
  position: absolute;
  height: 150px;
  top:50px; left:0; right:0;
  padding: 0 20px;
`
const ButtonBar = styled.div`
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
`

const ButtonGroup = styled(_ButtonGroup)`
  margin-right: 20px;
`

const ToolBar = ({
  variantFaceId,
  variantSimilarity,
  setVariantSimilarity,
  matchThreshold,
  setMatchThreshold,
  sessionId,
  faces,
  faceMatches,
  setFaceMatches,
  setIsLoading,
  isPageSelectedFaces=false,
  isPageLatestFaces=false,
  isPageSortFaces = false,
  makePredictions,
  imgHeight,
  setImgHeight,
  sortedFaces,
  selectedBaseFace,
}) => {
  const [hasSubmitted, setHasSubmitted] = useState(false)
  const storage = window.sessionStorage
  const [addSortedFaces] = useMutation(ADD_SORTED_FACES)
  const [generateRandomFaces] = useMutation(GENERATE_RANDOM_FACES)
  const [generatePredictedFaces] = useMutation(GENERATE_PREDICTED_FACES)
  const [generateVariantFaces] = useMutation(GENERATE_VARIANT_FACES)
  const [generateSortedFaces] = useMutation(GENERATE_SORTED_FACES)
  const [trainFaceMatches] = useMutation(ADD_FACE_MATCHES)
  const [trainSortedFaces] = useMutation(TRAIN_SORTED_FACES)
  const [resetSelections] = useMutation(RESET_SESSION)
  const [removeLatestFaces] = useMutation(REMOVE_LATEST_FACES)

  const onGenerateRandomFaces = useCallback(async () => {
    setIsLoading(true)
    await generateRandomFaces({
      variables: {
        input: {
          batchSize: 20,
          initNum: 5,
          trunc: 0.75
        }
      },
      refetchQueries: [{ query: LATEST_FACES }]
    })
    setIsLoading(false)
  }, [generateRandomFaces, sessionId])

  const onGeneratePredictedFaces = useCallback(async () => {
    setIsLoading(true)
    await generatePredictedFaces({
      variables: {
        matchThreshold
      },
      refetchQueries: [{ query: LATEST_FACES }]
    })
    setIsLoading(false)
  }, [generatePredictedFaces, sessionId, matchThreshold])

  const onGenerateVariantFaces = useCallback(async () => {
    setIsLoading(true)
    await generateVariantFaces({
      variables: {
        id: variantFaceId,
        similarity: variantSimilarity
      },
      refetchQueries: [{ query: LATEST_FACES }]
    })
    setIsLoading(false)
  }, [generateVariantFaces, sessionId, variantFaceId, variantSimilarity])

  const onReset = useCallback(async (input) => {
    await resetSelections({
      variables: {
        input
      },
      refetchQueries: [{ query: LATEST_FACES }]
    })
  }, [resetSelections, sessionId])

  const onGoBack = useCallback(async () => {
    await removeLatestFaces({
      refetchQueries: [{ query: LATEST_FACES }]
    })
  }, [removeLatestFaces, sessionId])

  const onTrain = useCallback(async ({ fineTune = false, train = true }) => {
    setIsLoading(true)
    const facesInput = _.reduce(faceMatches.matches, function (acc, value, key) {
      const item = {
        id: String(key),
        match: value
      }
      if ((fineTune && value) || (!fineTune && !_.isNil(value))) {
        acc.push(item)
      }
      return acc
    }, [])

    await trainFaceMatches({
      variables: {
        input: {
          fineTune,
          train,
          faces: facesInput
        }
      },
      refetchQueries: [
        { query: LATEST_FACES },
        { query: SELECTED_FACES }]
    })
    setIsLoading(false)
  }, [faces, faceMatches])

  const onBulkSelect = useCallback(() => {
    const ids = _.map(faces, 'id')
    const hasOne =_.some(faceMatches.matches, m => {
      return m === 1
    })
    const hasZero =_.some(faceMatches.matches, m => {
      return m === 0
    })
    if (hasZero) {
      setFaceMatches({ ids, idsVal: 1 })
    } else if (hasOne) {
      setFaceMatches({ ids, idsVal: null })
    } else {
      setFaceMatches({ ids, idsVal: 0 })
    }
  }, [faces, faceMatches, setFaceMatches])

  const adjustImgHeight = () => {
    if (imgHeight === '256px') setImgHeight('512px')
    if (imgHeight === '512px') setImgHeight('256px')
  }

  const onSubmitSortedFaces = async () => {
    setHasSubmitted(true)
    await addSortedFaces({
      variables: {
        input: {
          ids: sortedFaces,
        }
      },
      refetchQueries: []
    })
    console.log(sortedFaces)
  }

  const onTrainSortedFaces = useCallback(async ({ fineTune = false }) => {
    await trainSortedFaces({
      variables: {
        fineTune,
      },
      refetchQueries: []
    })
  }, [sessionId])

  const onGenerateSortedFaces = useCallback(async () => {
    setIsLoading(true)
    const variables = selectedBaseFace ? { id: selectedBaseFace.id } : {}
    await generateSortedFaces({
      variables,
      refetchQueries: [{ query: LATEST_FACES }]
    })
    setIsLoading(false)
  }, [sessionId, selectedBaseFace])

  if (isPageSortFaces) {
    return (
      <ShortWrapper>
        <ButtonBar>
          <ButtonGroup color="primary" aria-label="outlined primary button group">
            <Button onClick={onGenerateRandomFaces}>Random</Button>
            <Button onClick={onGenerateSortedFaces}>Generate</Button>
          </ButtonGroup>
          <ButtonGroup color="primary" aria-label="outlined primary button group">
            <Button onClick={onSubmitSortedFaces} disabled={hasSubmitted}>Submit</Button>
          </ButtonGroup>
          <ButtonGroup color="primary" aria-label="outlined primary button group">
            <Button onClick={() => onTrainSortedFaces({ fineTune: false })}>Train</Button>
            <Button onClick={() => onTrainSortedFaces({ fineTune: true })}>Fine-Tune</Button>
          </ButtonGroup>
        </ButtonBar>
      </ShortWrapper>
    )
  }

  if (isPageLatestFaces) {
    return (
      <Wrapper>
        <ButtonBar>
          <ButtonGroup color="primary" aria-label="outlined primary button group">
            <Button onClick={onGenerateRandomFaces} >Random</Button>
            <Button onClick={onGeneratePredictedFaces} >Predicted {matchThreshold}</Button>
            <Button onClick={onGenerateVariantFaces} >Variant</Button>
            <Button onClick={() => {
              if (variantSimilarity < 5) {
                setVariantSimilarity(variantSimilarity + 1)
              } else {
                setVariantSimilarity(0)
              }
            }} >{variantSimilarity}</Button>
          </ButtonGroup>
          <ButtonGroup color="primary" aria-label="outlined primary button group">
            <Button onClick={onBulkSelect}>Toggle Selections</Button>
            <Button onClick={() => onTrain({ train: false })}>Add Selections</Button>
            <Button onClick={() => onTrain({})}>Train</Button>
          </ButtonGroup>
          <ButtonGroup color="primary" aria-label="outlined primary button group">
            <Button onClick={() => onReset({ all: true })}>Start All</Button>
            <Button onClick={() => onReset({ no: true })}>Reset 'No'</Button>
            <Button onClick={onGoBack}>Go Back</Button>
          </ButtonGroup>
          <ButtonGroup color="primary" aria-label="outlined primary button group">
            <Button onClick={() => adjustImgHeight()}>Toggle Size</Button>
          </ButtonGroup>
        </ButtonBar>
        <MatchThreshold setMatchThreshold={setMatchThreshold} />
      </Wrapper>
    )
  }

  if (isPageSelectedFaces) {
    return (
      <Wrapper>
        <ButtonBar>
          <ButtonGroup color="primary" aria-label="outlined primary button group">
            <Button onClick={onGenerateVariantFaces} >Variant</Button>
            <Button onClick={() => {
              if (variantSimilarity < 5) {
                setVariantSimilarity(variantSimilarity + 1)
              } else {
                setVariantSimilarity(0)
              }
            }} >{variantSimilarity}</Button>
          </ButtonGroup>
          <ButtonGroup color="primary" aria-label="outlined primary button group">
            <Button onClick={makePredictions}>Update Predictions</Button>
          </ButtonGroup>
          <ButtonGroup color="primary" aria-label="outlined primary button group">
            <Button onClick={() => adjustImgHeight()}>Toggle Size</Button>
          </ButtonGroup>
        </ButtonBar>
      </Wrapper>
    )
  }
}

export default ToolBar


// const nClusters = 5
//
// const averageClusterMean = useMemo(() => {
//   return _.map(_.range(0, nClusters), i => {
//     const url = `/f8884cd6-401a-4cac-9557-4db0d1c43863/averages/1-${i}.png`
//     return (
//       <GridListTile key={`grid-list-mean-${i}`}>
//         <img key={`mean-image-${i}`} src={`${baseServerURL}${url}`} />
//         <GridListTileBar
//           style={{
//             height: '20px',
//             fontWeight: '900',
//             fontSize: '12em',
//             background: 'none'
//           }}
//           subtitle={<span style={{ background: 'none', color: 'white' }}>Mean: {i}</span>}
//         />
//       </GridListTile>
//     )
//   })
// }, [])
//
// const averageClusterCenter = useMemo(() => {
//   return _.map(_.range(0, nClusters), i => {
//     const url = `/f8884cd6-401a-4cac-9557-4db0d1c43863/averages/2-${i}.png`
//     return (
//       <GridListTile key={`grid-list-center-${i}`}>
//         <img key={`center-image-${i}`} src={`${baseServerURL}${url}`} />
//         <GridListTileBar
//           style={{
//             height: '20px',
//             fontWeight: '900',
//             fontSize: '12em',
//             background: 'none'
//           }}
//           subtitle={<span style={{ background: 'none', color: 'white' }}>Center: {i}</span>}
//         />
//       </GridListTile>
//     )
//   })
// }, [])
//
// const onGenerateAveragedFaces = useCallback(async () => {
//   setIsLoading(true)
//   await generateAveragedFaces({
//     refetchQueries: [{ query: LATEST_FACES }]
//   })
//   setIsLoading(false)
// }, [generateAveragedFaces, sessionId])
