import React, { useEffect, useState } from 'react'
import { useQuery } from '@apollo/client'
import _ from 'lodash'
import {
  Grid,
  GridList,
  GridListTile,
  GridListTileBar,
} from '@material-ui/core'
import styled from 'styled-components/macro'
import { baseServerURL } from '../config'
import { LATEST_FACES } from "../queries"
import ToolBar from "../components/ToolBar"
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  horizontalListSortingStrategy,
} from '@dnd-kit/sortable'


import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

const Wrapper = styled.div`
  position: absolute;
  top: 100px;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: scroll;
`

const Content = styled.div`
  display: flex;
  flex-wrap: wrap;
  padding: 0;
  margin: 0;
  line-height: 0;
`

const SortableItem = (props) => {
  const { selectedBaseFace, setSelectedBaseFace } = props
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id: props.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <Face
        face={props.face}
        selectedBaseFace={selectedBaseFace}
        setSelectedBaseFace={setSelectedBaseFace}/>
    </div>
  )
}

const Face = ({
  face,
  imgHeight = '350px',
  selectedBaseFace,
  setSelectedBaseFace,
}) => {
  if (!face) return null
  const { id, url, prediction = 0 } = face
  let bg = 'rgba(255, 255, 255, .5)'
  if (face === selectedBaseFace) {
    bg = 'rgba(0, 255, 0, .5)'
  }
  const handleClick = () => {
    if (face !== selectedBaseFace) setSelectedBaseFace(face)
    else setSelectedBaseFace(null)
  }
  return (
    <GridListTile
      col={1}
      row={1}
      style={{
        padding: '0px',
        height: imgHeight,
        listStyleType: 'none' }}>
      <img
        style={{
          userSelect: 'none',
          height: imgHeight,
          width: imgHeight,
        }}
        key={`select-image-${url}`}
        src={`${baseServerURL}${url}`}
      />
      <GridListTileBar
        onClick={handleClick}
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
            {_.round(prediction, 5)}
          </span>
        }
      />
    </GridListTile>

  )
}

const SelectFaces = () => {
  const [faces, setFaces] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const { loading, data } = useQuery(LATEST_FACES, {
    fetchPolicy: 'network-only'
  })

  useEffect(() => {
    if (data?.latestFaces) {
      const _faces = data.latestFaces.slice(0, 10)
      setFaces(_faces)
      setIsLoading(false)
    }
  }, [data])

  const sessionId = data?.session || 'No sessionId found'

  if (_.isEmpty(faces) || loading ) return null

  return (
    <SortableFaces faces={faces} sessionId={sessionId} setIsLoading={setIsLoading} isLoading={isLoading} />
  )
}

const SortableFaces = ({ faces, sessionId, setIsLoading, isLoading }) => {
  const facesById = _.groupBy(faces, 'id')
  const [items, setItems] = useState([])
  const [selectedBaseFace, setSelectedBaseFace] = useState(null)
  const sensors = useSensors(
    useSensor(PointerSensor),
  )

  useEffect(() => {
    if (faces) {
      const sortedFaces = _.reverse(_.sortBy(faces, 'prediction'))
      const faceIds = _.map(sortedFaces, 'id')
      setItems(faceIds)
    }
  }, [faces])

  useEffect(() => {
    if (isLoading) setItems([])
  }, [isLoading])

  if (isLoading) {
    return <h1>Loading...</h1>
  }

  return (
    <>
      <ToolBar {...{
        sessionId,
        faces,
        sortedFaces: items,
        isPageSortFaces: true,
        selectedBaseFace,
        setIsLoading,
      }} />
      <Wrapper>
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={items}
            strategy={horizontalListSortingStrategy}
          >
            <Content>
              {items.map(id => <SortableItem
                key={id}
                id={id}
                face={facesById[id][0]}
                selectedBaseFace={selectedBaseFace}
                setSelectedBaseFace={setSelectedBaseFace}
              />)}
            </Content>
          </SortableContext>
        </DndContext>
      </Wrapper>
    </>

  )

  function handleDragEnd(event) {
    const { active, over } = event

    if (active.id !== over.id) {
      setItems((items) => {
        const oldIndex = items.indexOf(active.id)
        const newIndex = items.indexOf(over.id)

        return arrayMove(items, oldIndex, newIndex)
      })
    }
  }

}

export default SelectFaces
