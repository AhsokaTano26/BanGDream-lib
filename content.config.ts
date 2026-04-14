import { defineContentConfig, defineCollection, z } from '@nuxt/content'

// 定义通用的组织枚举
const orgEnum = z.enum([
  "ppp", "a", "pp", "R", "HHP", "M", "RAS", "mygo", "Ave", "mxd", "millsage", "dumb", "Shuffle", "other"
])

export default defineContentConfig({
  collections: {
    // 对应 Blog(Live/Event)
    blog: defineCollection({
      type: 'page',
      source: 'blog/**',
      schema: z.object({
        title: z.string(),
        description: z.string(),
        date: z.string(),
        status: z.enum(["on_site ", "activity", "other"]), // 注意文件中有个空格
        author: z.string(),
        location: z.string(),
        org: z.array(orgEnum),
        url: z.string().url()
      })
    }),

    // 对应 News(News)
    news: defineCollection({
      type: 'page',
      source: 'news/**',
      schema: z.object({
        title: z.string(),
        description: z.string(),
        date: z.string(),
        status: z.enum(["notice", "on_site ", "publish", "product", "media"]),
        org: z.array(orgEnum),
        url: z.string().url()
      })
    }),

    // 对应 Notice(官方公告)
    notice: defineCollection({
      type: 'page',
      source: 'notice/**',
      schema: z.object({
        title: z.string(),
        description: z.string(),
        date: z.string(),
        author: z.string()
      })
    }),

    // 对应 Timeline(timeline)
    timeline: defineCollection({
      type: 'page',
      source: 'timeline/**',
      schema: z.object({
        title: z.string(),
        description: z.string(),
        date: z.string(),
        author: z.string(),
        type: z.enum(["official", "anniversary", "daily", "other"])
      })
    }),

    // 对应 Discographies(Discographies)
    discographies: defineCollection({
      type: 'page',
      source: 'discographies/**',
      schema: z.object({
        title: z.string(),
        description: z.string(),
        date: z.string(),
        status: z.enum(["cd", "bd", "bp", "music", "mj"]),
        author: z.string(),
        org: z.array(orgEnum),
        url: z.string().url()
      })
    }),

    // 对应 Media(Media)
    media: defineCollection({
      type: 'page',
      source: 'media/**',
      schema: z.object({
        title: z.string(),
        description: z.string(),
        date: z.string(),
        type: z.enum(["radio", "online", "tv", "article", "comic"]),
        author: z.string(),
        org: z.array(orgEnum),
        url: z.string().url(),
        status: z.enum(["finish", "stop"])
      })
    }),

    // 对应 Org(Band)
    orgs: defineCollection({
      type: 'page',
      source: 'orgs/**',
      schema: z.object({
        title: z.string(),
        description: z.string(),
        founded: z.string(),
        theme: z.object({
          logo: z.string().nullable().optional(),
          bgImage: z.string().nullable().optional(),
          primaryColor: z.string()
        })
      })
    }),

    // 对应 Artist(Artist)
    artist: defineCollection({
      type: 'page',
      source: 'artist/**',
      schema: z.object({
        title: z.string(),
        description: z.string(),
        date: z.string(),
        author: z.string(),
        org: z.array(orgEnum),
        url: z.string().url()
      })
    })
  }
})