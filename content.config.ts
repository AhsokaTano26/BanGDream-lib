import { defineContentConfig, defineCollection, z } from '@nuxt/content'

export default defineContentConfig({
    collections: {
        blog: defineCollection({
            type: 'page',
            // 默认指向 content/blog/**
            source: 'blog/**',
            schema: z.object({
                title: z.string(),
                date: z.string(),
                description: z.string(),
                author: z.string(),
                type: z.string(),
            })
        }),
        timeline: defineCollection({
            type: 'page',
            source: 'timeline/**',
            schema: z.object({
                title: z.string(),
                date: z.string(),
                description: z.string(),
                author: z.string(),
                status: z.string(),
            })
        }),
        projects: defineCollection({
            type: 'page',
            source: 'projects/**',
            schema: z.object({
                title: z.string(),
                description: z.string(),
                orgs: z.string(),
                date: z.string(),
                author: z.string(),
                status: z.string(),
                link: z.string().optional(),
            })
        }),
        orgs: defineCollection({
            type: 'page',
            source: 'orgs/**',
            schema: z.object({
                orgs_id: z.string(),
                title: z.string(),
                description: z.string(),
                founded: z.string(),
                joined_at: z.string(),
                members_count: z.string(),
                website: z.string().optional(),
                github: z.string().optional(),
                status: z.string(),
                leader: z.string(),
                location: z.string(),
                type: z.string(),
                tag: z.string(),
                theme: z.object({
                    logo: z.string().optional(),
                    primaryColor: z.string().optional(),
                    bgImage: z.string().optional(),
                    bgOverlayOpacity: z.number().optional(),
                    sidebarOpacity: z.number().optional(),
                    mainOpacity: z.number().optional(),
                    rightTickOpacity: z.number().optional(),
                })
            })
        }),
        notice: defineCollection({
            type: 'page',
            source: 'notice/**',
            schema: z.object({
                title: z.string(),
                date: z.string(),
                description: z.string(),
                author: z.string(),
                type: z.string(),
            })
        }),
        activities: defineCollection({
            type: 'page',
            source: 'activities/**',
            schema: z.object({
                title: z.string(),
                date: z.string(),
                status: z.string(),
                org: z.string(),
                author: z.string(),
                type: z.string(),
            })
        }),
        archive: defineCollection({
            type: 'page',
            source: 'archive/**',
            schema: z.object({
                title: z.string(),
                description: z.string(),
                orgs: z.string(),
                date: z.string(),
                author: z.string(),
                type: z.string(),
            })
        }),
    }
})