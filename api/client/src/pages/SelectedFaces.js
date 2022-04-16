import React, { useEffect, useCallback, useState, useMemo, useReducer } from 'react'
import { useQuery, useMutation } from '@apollo/client'
import _ from 'lodash'
import {
  Grid,
  GridList,
  GridListTile,
  GridListTileBar,
} from '@material-ui/core'
import styled from 'styled-components/macro'
import { baseServerURL } from '../config'
import { MAKE_PREDICTIONS, SELECTED_FACES } from "../queries"
import ToolBar from "../components/ToolBar"

const Content = styled.div`
  position: absolute;
  top: 155px;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: scroll;
`

const faceMatchReducer = ({ matches }, { id, idsVal, ids, reset }) => {
  if (reset) {
    return { matches: {} }
  }
  if (ids) {
    _.each(ids, id => {
      if (!_.isNil(idsVal)) matches[id] = idsVal
      else delete matches[id]
    })
    return { matches }
  }
  if (_.isNil(matches[id])) matches[id] = 0
  else if (matches[id] < 1) matches[id] += 1
  else delete matches[id]
  return { matches }
}

const imageEls = ({
  faces,
  setFaceMatches,
  variantFaceId,
  variantSimilarity,
  setVariantSimilarity,
  setVariantFaceId,
  imgHeight = '256px',
}) => {
  const sortedFaces = _.reverse(_.sortBy(faces, 'prediction'))
  return _.map(sortedFaces, face => {
    const { id, url, prediction = 0 } = face
    const RGBs = [
      'rgba(255, 0, 0, .5)',
      'rgba(0, 255, 0, .5)',
    ]
    let bg = RGBs[prediction > .5 ? 1 : 0] || 'rgba(255, 255, 255, .5)'
    if (id === variantFaceId) {
      bg = `rgba(128,0,128, ${variantSimilarity * 0.1})`
    }
    return (
      <Grid item>
        <GridList cols={1} cellHeight='auto' style={{ margin: '0', padding: '0' }}>
          <GridListTile col={1} row={1} style={{ padding: '0', height: imgHeight }}>
            <img
              style={{
                userSelect: 'none',
                height: imgHeight,
                width: imgHeight,
              }}
              key={`select-image-${id}`}
              src={`${baseServerURL}${url}`}
              onClick={() => setFaceMatches({ id })}
            />
            <GridListTileBar
              onClick={() => {
                if (variantFaceId !== id) {
                  setVariantSimilarity(1)
                  setVariantFaceId(id)
                } else if (variantSimilarity < 10) {
                  setVariantSimilarity(variantSimilarity + 1)
                } else {
                  setVariantSimilarity(0)
                  setVariantFaceId(null)
                }
              }}
              style={{
                height: '20px',
                fontWeight: '900',
                fontSize: '12em',
                background: `${bg}`
              }}
              subtitle={
                <span
                  style={{
                    background: 'black',
                    color: 'white',
                    userSelect: 'none'
                  }}
                >
                  {_.round(prediction, 5)}{ variantFaceId === id ? ` - ${variantSimilarity}` : ''}
                </span>
              }
            />
          </GridListTile>
        </GridList>
      </Grid>
    )
  })
}

const SelectFaces = () => {
  const [isLoading, setIsLoading] = useState()
  const [imgHeight, setImgHeight] = useState("256px")
  const [faces, setFaces] = useState([])
  const [faceMatches, setFaceMatches] = useReducer(faceMatchReducer, { matches: {} })
  const [matchThreshold, setMatchThreshold] = useState(0.5)

  const [variantFaceId, setVariantFaceId] = useState()
  const [variantSimilarity, setVariantSimilarity] = useState(0)

  const { loading, data } = useQuery(SELECTED_FACES, {
    fetchPolicy: 'network-only'
  })

  const [makePredictions] = useMutation(MAKE_PREDICTIONS, {
    variables: {
      ids: _.map(faces, 'id')
    },
    refetchQueries: [{ query: SELECTED_FACES }]
  })

  useEffect(() => {
    setIsLoading(loading)
  }, [loading])


  const sessionId = data?.session || 'No sessionId found'

  useEffect(() => {
    if (data?.selectedFaces) {
      const _faces = data.selectedFaces
      setFaceMatches({ reset: true })
      setFaces(_faces)
    }
  }, [data])

  useEffect(() => {
    const matches = {}
    for (let i = 0; i < faces.length; i++) {
      const face = faces[i]
      matches[face.id] = face.prediction >= matchThreshold ? 1 : 0
    }
    setFaceMatches(matches)
  }, [faces, matchThreshold])

  if (isLoading) return (
    <h1>Loading</h1>
  )

  return (
    <>
      <ToolBar {...{
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
        isPageSelectedFaces: true,
        makePredictions,
        imgHeight,
        setImgHeight,
      }} />

      <Content>
        <Grid container spacing={1}>
          {imageEls({
            faces,
            faceMatches,
            setFaceMatches,
            variantFaceId,
            variantSimilarity,
            setVariantSimilarity,
            setVariantFaceId,
            imgHeight
          })}
        </Grid>
      </Content>
    </>
  )
}

export default SelectFaces
