import React from 'react'
import {
  Slider
} from '@material-ui/core'
import styled from 'styled-components/macro'

const SliderWrapper = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
`

const MatchThreshold = ({ setMatchThreshold }) => {
  const handleChange = (e, n) => {
    setMatchThreshold(n)
  }

  return (
    <SliderWrapper>
      <Slider
        defaultValue={0.5}
        aria-labelledby="discrete-slider"
        valueLabelDisplay="auto"
        step={0.01}
        min={0.05}
        max={0.99}
        onChange={handleChange}
      />
    </SliderWrapper>

  )
}

export default MatchThreshold
