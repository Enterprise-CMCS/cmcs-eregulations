import {rest } from 'msw'
import {partToc42, partToc45} from "../mocks/part_toc.js"
import {titles} from "../mocks/titles.js"

export const handlers = [
    rest.get('*/title/42/parts',( req, res, ctx) => {
        return res(ctx.status(200), ctx.json(partToc42))
    }),
    rest.get('*/title/45/parts',( req, res, ctx) => {
        return res(ctx.status(200), ctx.json(partToc45))
    }),
    rest.get('*/titles', (req, res, ctx)=> {
        return res(ctx.status(200), ctx.json(titles))
    })
]