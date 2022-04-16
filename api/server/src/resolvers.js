const fs = require('fs')
const _ = require('lodash')
const { chain }  = require('stream-chain')
const { parser } = require('stream-json')
const { streamArray } = require('stream-json/streamers/StreamArray')
const Redis = require('ioredis')

const redisOptions = {
  host: '127.0.0.1',
  port: 6379,
  db: 1,
  retryStrategy: times => {
    return Math.min(times * 50, 2000)
  },
}

const redis = new Redis(redisOptions)

const EXPERIMENTS_DIR = "/scratch/experiments"
let lastMatchThreshold

const generateRandomFaces = (args, sessionId) => {
  const { batchSize, trunc, initNum } = args
  let { PythonShell } = require('python-shell')
  return new Promise((resolve, reject) => {
    let lastMessage
    let options = {
      mode: 'text',
      pythonPath: '/opt/conda/bin/python',
      pythonOptions: ['-u'], // get print results in real-time
      scriptPath: '/scratch',
      args: [
        "--truncation_psi", trunc,
        "--network", "https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl",
        "--batch_size", batchSize,
        "--init_num", initNum,
        "--session_id", sessionId,
      ]
    }

    let pyshell = new PythonShell('generate_random_faces.py', options)

    pyshell.on('message', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.log(message)
      lastMessage = message
    })

    pyshell.on('stderr', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.error(message)
    })

    pyshell.on('close', function () {
      // received a message sent from the Python script (a simple "print" statement)
      console.log('Python has exited')
      resolve(lastMessage)
    })
  })

}

const generateVariantFaces = (args = {}, sessionId) => {
  const { batchSize = 5, trunc = .75, gBatchSize = 50, numFaces = 100, id, similarity = 1 } = args
  // const { batchSize = 20, trunc = .75, gBatchSize = 50, targetNum = 100, id, similarity = 1 } = args
  let { PythonShell } = require('python-shell')
  return new Promise((resolve, reject) => {
    let lastMessage
    let options = {
      mode: 'text',
      pythonPath: '/opt/conda/bin/python',
      pythonOptions: ['-u'], // get print results in real-time
      scriptPath: '/scratch',
      args: [
        "--truncation_psi", trunc,
        "--network", "https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl",
        "--batch_size", batchSize,
        "--session_id", sessionId,
        "--g_batch_size", gBatchSize,
        "--target_face_id", id,
        "--num_faces", numFaces,
        "--similarity", similarity,
      ]
    }

    let pyshell = new PythonShell('generate_variant_faces.py', options)

    pyshell.on('message', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.log(message)
      lastMessage = message
    })

    pyshell.on('stderr', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.error(message)
    })

    pyshell.on('close', function () {
      // received a message sent from the Python script (a simple "print" statement)
      console.log('Python has exited')
      resolve(lastMessage)
    })
  })
}

const generatePredictedFaces = (args = {}, sessionId) => {
  const {
    batchSize = 100,
    trunc = .75,
    numFaces = 100,
    gBatchSize = 50,
    matchThreshold = 1.0
  } = args
  let { PythonShell } = require('python-shell')
  return new Promise((resolve) => {
    let lastMessage
    let options = {
      mode: 'text',
      pythonPath: '/opt/conda/bin/python',
      pythonOptions: ['-u'], // get print results in real-time
      scriptPath: '/scratch',
      args: [
        "--truncation_psi", trunc,
        "--network", "https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl",
        "--batch_size", batchSize,
        "--session_id", sessionId,
        "--num_faces", numFaces,
        "--match_threshold", matchThreshold,
        "--g_batch_size", gBatchSize,
      ]
    }

    let pyshell = new PythonShell('generate_predicted_faces.py', options)

    pyshell.on('message', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.log(message)
      lastMessage = message
    })

    pyshell.on('stderr', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.error(message)
    })

    pyshell.on('close', function () {
      // received a message sent from the Python script (a simple "print" statement)
      console.log('Python has exited')
      resolve(lastMessage)
    })
  })

}

const generateSortedFaces = (args = {}, sessionId) => {
  const {
    id: baseFaceId,
    trunc = .65,
    numFaces = 10,
  } = args
  let { PythonShell } = require('python-shell')
  return new Promise((resolve) => {
    let lastMessage
    let options = {
      mode: 'text',
      pythonPath: '/opt/conda/bin/python',
      pythonOptions: ['-u'], // get print results in real-time
      scriptPath: '/scratch',
      args: [
        "--truncation_psi", trunc,
        "--network", "https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl",
        "--session_id", sessionId,
        "--num_faces", numFaces,
        "--base_face_id", baseFaceId,
      ]
    }

    let pyshell = new PythonShell('generate_sorted_faces.py', options)

    pyshell.on('message', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.log(message)
      lastMessage = message
    })

    pyshell.on('stderr', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.error(message)
    })

    pyshell.on('close', function () {
      // received a message sent from the Python script (a simple "print" statement)
      console.log('Python has exited')
      resolve(lastMessage)
    })
  })

}

const makePredictions = (args = {}, sessionId) => {
  const {
    ids = []
  } = args
  let { PythonShell } = require('python-shell')
  console.log(`predict num ids: ${ids.length}`)
  return new Promise((resolve) => {
    let lastMessage
    const args = [
      "--session_id", sessionId,
      "--ids", ...ids,
    ]

    let options = {
      mode: 'text',
      pythonPath: '/opt/conda/bin/python',
      pythonOptions: ['-u'], // get print results in real-time
      scriptPath: '/scratch',
      args,
    }

    let pyshell = new PythonShell('get_predictions_by_ids.py', options)

    pyshell.on('message', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.log(message)
      lastMessage = message
    })

    pyshell.on('stderr', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
      console.error(message)
    })

    pyshell.on('close', function () {
      // received a message sent from the Python script (a simple "print" statement)
      console.log('Python has exited')
      resolve(lastMessage)
    })
  })

}

const trainModel = (input, sessionId) => {
  // const { batchSize = 10, trunc = .75, fineTune = false } = input
  // At larger amounts of data, a bigger batch size trains better, with lr of .00008 (vs. 00002 for lower sized batches)
  const { trunc = .75, fineTune = false } = input
  let { PythonShell } = require('python-shell')
  let args = [
    "--truncation_psi", trunc,
    "--network", "https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl",
    "--session_id", sessionId
  ]
  if (fineTune) {
    args.push('--fine_tune')
    args.push('True')
  }
  return new Promise((resolve) => {
    let options = {
      mode: 'text',
      pythonPath: '/opt/conda/bin/python',
      pythonOptions: ['-u'], // get print results in real-time
      scriptPath: '/scratch',
      args,
    }

    let pyshell = new PythonShell('train_face_matches.py', options)

    pyshell.on('message', function (message) {
      console.log(message)
    })

    pyshell.on('stderr', function (message) {
      console.error(message)
    })

    pyshell.on('close', function () {
      console.log('Python has exited')
      resolve()
    })
  })

}

const trainSortedFaces = (args, sessionId) => {
  const { fineTune = false } = args
  let { PythonShell } = require('python-shell')
  let pythonArgs = [
    "--truncation_psi", .75,
    "--network", "https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl",
    "--session_id", sessionId,
  ]
  if (fineTune) {
    pythonArgs.append('--fine_tune')
  }

  return new Promise((resolve) => {
    let options = {
      mode: 'text',
      pythonPath: '/opt/conda/bin/python',
      pythonOptions: ['-u'], // get print results in real-time
      scriptPath: '/scratch',
      args: pythonArgs,
    }

    let pyshell = new PythonShell('train_sorted_faces.py', options)

    pyshell.on('message', function (message) {
      console.log(message)
    })

    pyshell.on('stderr', function (message) {
      console.error(message)
    })

    pyshell.on('close', function () {
      console.log('Python has exited')
      resolve()
    })
  })

}


const resolvers = {
  Query: {
    session: async (parent, args, { sessionId }) => {
      return sessionId || "No session"
    },
    latestFaces: async (parent, args, { sessionId }) => {
      return new Promise((resolve, reject) => {
        fs.readFile(`${EXPERIMENTS_DIR}/${sessionId}/data/faces.json`, (err, data) => {
          try {
            if (data) {
              let faces = JSON.parse(data)
              faces = _.last(faces)
              faces = _.groupBy(_.flatten(faces), 'id')
              faces = _.map(faces, v => _.last(v))
              resolve(faces)
            } else {
              resolve([])
            }
          } catch (e) {
            console.log(e)
            resolve([])
          }
        })
      })
    },
    selectedFaces: async (parent, args, { sessionId }) => {
      const matchesPath = `${EXPERIMENTS_DIR}/${sessionId}/data/matches.json`
      const facesPath = `${EXPERIMENTS_DIR}/${sessionId}/data/faces.json`
      const fixedFacesPath = `${EXPERIMENTS_DIR}/${sessionId}/data/faces-fixed.json`

      // // Fix faces file
      // let faceIds = await new Promise((resolve) => {
      //   fs.readFile(matchesPath, (err, data) => {
      //     try {
      //       if (data) {
      //         let selections = JSON.parse(data)
      //         selections = _.flattenDeep(selections)
      //         console.log(selections.length)
      //         let ids = _.map(selections, 'id')
      //         ids = _.uniq(ids)
      //         resolve(ids)
      //       } else {
      //         resolve({ errors: [] })
      //       }
      //     } catch (e) {
      //       console.log(e)
      //       resolve([{ errors: ["We had some kind of problem"] }])
      //     }
      //   })
      // })
      // console.log('faceIds length', faceIds.length)
      //
      // return new Promise((resolve, reject) => {
      //   console.log('Creating pipeline')
      //   let fixedFaces = []
      //   try {
      //     const pipeline = chain([
      //       fs.createReadStream(facesPath),
      //       parser(),
      //       streamArray(),
      //     ])
      //     console.log('Pipeline created')
      //     let count = 0
      //     pipeline.on('data', (data) => {
      //       count += 1
      //       let faces = data.value
      //       faces = _.keyBy(faces, 'id')
      //       fixedFaces.push(_.values(faces))
      //       // allFaces = _.merge(allFaces, faces)
      //       console.log(count, data.value.length, _.values(faces).length)
      //     })
      //     pipeline.on('end', () => {
      //       console.log('Finished', count, fixedFaces.length, _.flattenDeep(fixedFaces).length)
      //       // const selectedFaces = _.pick(allFaces, faceIds)
      //       fs.writeFileSync(fixedFacesPath, JSON.stringify(fixedFaces))
      //       resolve({ errors: [] })
      //     })
      //   } catch (e) {
      //     console.log(e)
      //     resolve({ errors: [] })
      //   }
      //
      // })
      //
      const faces = await new Promise((resolve) => {
        let allFaces = []
        count = 0
        try {
          const pipeline = chain([
            fs.createReadStream(facesPath),
            parser(),
            streamArray(),
          ])
          pipeline.on('data', (data) => {
            count += 1
            let faces = data.value
            let filteredFaces = _.keyBy(faces, 'id')
            // console.log(count, faces.length, _.values(filteredFaces).length)
            allFaces.push(_.values(filteredFaces))
          })
          pipeline.on('end', () => {
            resolve(allFaces)
          })
        } catch (e) {
          console.log(e)
          resolve({ errors: [] })
        }

      })
      return new Promise((resolve) => {
        try {
          const facesById = _.groupBy(_.flatten(faces), 'id')
          // console.log(`Found ${_.keys(facesById).length} faces`)
          fs.readFile(matchesPath, (err, data) => {
            try {
              if (data) {
                const allSelections = JSON.parse(data)
                // console.log(`Found ${_.flattenDeep(allSelections).length} selections`)
                let selectedFaces = {}
                _.each(allSelections, mSet => {
                  _.each(mSet, m => {
                    // If we went 'back', any matches are lost unfortunately...
                    if (facesById[m.id]) {
                      if (m.match === 1) {
                        selectedFaces[m.id] = _.last(facesById[m.id])
                      }
                      if (m.match === 0) {
                        delete selectedFaces[m.id]
                      }
                    }
                  })
                })
                selectedFaces = _.map(selectedFaces, v => v)
                resolve(selectedFaces)
              } else {
                resolve({ errors: [] })
              }
            } catch (e) {
              console.log(e)
              resolve([{ errors: ["We had some kind of problem"] }])
            }
          })
        } catch (e) {
          console.log('error', e)
          resolve([])
        }
      })
    },
  },
  Mutation: {
    addSortedFaces: async (parent, { input: { ids = [] } }, { sessionId }) => {
      const nRunsKey = `sorted_faces:${sessionId}:run`
      const nRuns = await redis.incr(nRunsKey)
      const runKey = `sorted_faces:${sessionId}:${nRuns}`
      const run = JSON.stringify(ids)
      await redis.set(runKey, run)
      return { errors: [] }
    },
    makePredictions: async (parent, args, { sessionId }) => {
      await makePredictions(args, sessionId)
      return { errors: [] }
    },
    resetSelections: async (parent, { input: { all, matches, yes, no } }, { sessionId }) => {
      const matchesPath = `${EXPERIMENTS_DIR}/${sessionId}/data/matches.json`
      if (matches) {
        try {
          fs.unlinkSync(matchesPath)
          return { errors: [] }
        } catch (err) {
          return { errors: ["Couldn't remove matches file"] }
        }
      }
      if (yes || no) {
        let keepMatchValues = yes ? 0 : 1
        return new Promise((resolve) => {
          fs.readFile(matchesPath, (err, data) => {
            try {
              if (data) {
                const matches = JSON.parse(data)
                let allMatchObj = {}
                _.each(matches, mSet => {
                  _.each(mSet, m => {
                    // Ensures latest value is provided for the id
                    allMatchObj[m.id] = m
                  })
                })
                allMatchObj = _.map(allMatchObj, o => o)
                allMatchObj = _.filter(allMatchObj, o => o.match === keepMatchValues)
                fs.writeFileSync(matchesPath, JSON.stringify([allMatchObj]))
                resolve({ errors: [] })
              } else {
                resolve([{ errors: [] }])
              }
            } catch (e) {
              console.log(e)
              resolve([{ errors: ["We had some kind of problem"] }])
            }
          })
        })
      }
      if (all) {
        new Promise((resolve, reject) => {
          fs.rmdir(`${EXPERIMENTS_DIR}/${sessionId}`, { recursive: true }, (err) => {
            if (err) {
              resolve({ errors: ["Couldn't delete directory"] })
            }
            resolve({ errors: [] })
          })
        })
      }
    },
    generateRandomFaces: async (parent, { input }, { sessionId }) => {
      await generateRandomFaces(input, sessionId)
      return { errors: [] }
    },
    generateVariantFaces: async (parent, args, { sessionId }) => {
      await generateVariantFaces(args, sessionId)
      return { errors: [] }
    },
    generatePredictedFaces: async (parent, args, { sessionId }) => {
      if (args.matchThreshold !== lastMatchThreshold) {
        try {
          fs.unlinkSync(`${EXPERIMENTS_DIR}/${sessionId}/data/G.pt`)
          lastMatchThreshold = args.matchThreshold
        } catch (err) {
        }
      }
      await generatePredictedFaces(args, sessionId)
      return { errors: [] }
    },
    generateSortedFaces: async (parent, args, { sessionId }) => {
      await generateSortedFaces(args, sessionId)
      return { errors: [] }
    },
    removeLatestFaces: async (parent, args, { sessionId }) => {
      const facesPath = `${EXPERIMENTS_DIR}/${sessionId}/data/faces.json`
      return new Promise((resolve, reject) => {
        fs.readFile(facesPath, (err, data) => {
          try {
            if (data) {
              const faces = JSON.parse(data)
              faces.pop()
              fs.writeFileSync(facesPath, JSON.stringify(faces))
              resolve({ errors: [] })
            } else {
              resolve([{ errors: [] }])
            }
          } catch (e) {
            resolve([{ errors: ["We had some kind of problem"] }])
          }
        })
      })
    },
    trainFaceMatches: async (parent, { input }, { sessionId }) => {
      const filePath = `${EXPERIMENTS_DIR}/${sessionId}/data/matches.json`
      const newMatches = _.get(input, 'faces', [])
      const prevMatchesPromise = new Promise((resolve, reject) => {
        fs.readFile(filePath, (err, data) => {
          try {
            if (data) {
              const prevMatches = JSON.parse(data)
              resolve(prevMatches)
            } else {
              resolve([])
            }
          } catch (e) {
            resolve([])
          }
        })
      })
      let matches = await prevMatchesPromise
      matches.push(newMatches)
      fs.writeFileSync(filePath, JSON.stringify(matches))
      if (input.train) {
        await trainModel(input, sessionId)
      }
      return { errors: [] }
    },
    trainSortedFaces: async (parent, args, { sessionId }) => {
      await trainSortedFaces(args, sessionId)
      return { errors: [] }
    },
  }
}

module.exports = {
  resolvers,
}
