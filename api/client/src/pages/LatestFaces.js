import React, { useEffect, useState, useReducer } from 'react'
import { useQuery } from '@apollo/client'
import _ from 'lodash'
import {
  Grid,
  GridListTile,
  GridListTileBar,
  GridList,
} from '@material-ui/core'
import styled from 'styled-components/macro'
import { baseServerURL } from '../config'
import { LATEST_FACES } from "../queries"
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
  faceMatches,
  setFaceMatches,
  variantFaceId,
  variantSimilarity,
  setVariantSimilarity,
  setVariantFaceId,
  imgHeight = "256px"
}) => {
  const sortedFaces = _.reverse(_.sortBy(faces, 'prediction'))
  return _.map(sortedFaces, face => {
    const { id, url, prediction = 0 } = face
    const RGBs = [
      'rgba(255, 0, 0, .5)',
      'rgba(0, 255, 0, .5)',
    ]
    const matchVal = faceMatches.matches[id]
    let bg = RGBs[matchVal] || 'rgba(255, 255, 255, .5)'
    if (id === variantFaceId) {
      bg = `rgba(128,0,128, ${variantSimilarity * 0.1})`
    }
    return (
      <Grid key={`grid-list-${id}`} item>
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

const LatestFaces = () => {
  const [isLoading, setIsLoading] = useState()
  const [imgHeight, setImgHeight] = useState("256px")
  const [faces, setFaces] = useState([])
  const [faceMatches, setFaceMatches] = useReducer(faceMatchReducer, { matches: {} })
  const [matchThreshold, setMatchThreshold] = useState(0.5)

  const [variantFaceId, setVariantFaceId] = useState()
  const [variantSimilarity, setVariantSimilarity] = useState(0)

  const { loading, data } = useQuery(LATEST_FACES, {
    fetchPolicy: 'network-only'
  })

  useEffect(() => {
    setIsLoading(loading)
  }, [loading])

  const sessionId = data?.session || 'No sessionId found'

  useEffect(() => {
    if (data?.latestFaces) {
      const _faces = data.latestFaces
      setFaceMatches({ reset: true })
      setFaces(_faces)
    }
  }, [data, setFaceMatches])

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
        isPageLatestFaces: true,
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

export default LatestFaces
