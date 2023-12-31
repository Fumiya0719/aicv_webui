<script setup lang="ts">
import HeaderComponent from '@/components/HeaderComponent.vue'
import ButtonComponent from '@/components/ButtonComponent.vue'

import { ref, onMounted } from 'vue'
import ApiManager from '@/server/apiManager'
import { PixPostInfo, PixPostImage } from '@/types'
import { PixSearch } from '@/types'
import { apiPath } from '@/assets/ts/paths'

import '@/assets/scss/imagedler/pixForm.scss'

const errorMessage = ref<string>('')
const search = ref<PixSearch>({
    userID: 0,
    tag: '',
    getPostType: 'tag',
    getNumberOfPost: '250',
    minBookmarks: 2000,
    isGetFromPreviousPost: false,
    includeTags: false,
    suspendID: '',
    isIgnoreSensitive: true,
})

// pixivユーザーID・中断IDを取得
const apiManager = new ApiManager()
const getUserInfo = async () => {
    const response = await apiManager.get(`${apiPath}/api/getPixivInfo`)
    return response.content.content
}

// 入力フォームのバリデーション
const inputValidation = (): string => {
    let error = ''
    if (search.value.userID === null || search.value.userID === 0) {
        error = 'ユーザーIDが入力されていません。'
    }

    const numPost = parseInt(search.value.getNumberOfPost)
    if (isNaN(numPost)) {
        error = '取得作品数は数値で入力してください。'
    }
    if (numPost < 10 || numPost > 300) {
        error = '取得できる作品の最小値は10, 最大値は300です。'
    }
    return error
}

const pixPostInfo = ref<PixPostInfo[]>([])
const isLoadImages = ref<boolean>(false)
const dlName = ref<string>('')
// 画像情報の取得
const getImage = async () => {
    isLoadImages.value = true
    errorMessage.value = inputValidation()
    if (errorMessage.value !== '') return

    const response = await apiManager.post(`${apiPath}/pixiv/getImages`, {
        content: search.value,
    })

    pixPostInfo.value = response.map((post: PixPostInfo) => {
        return {
            postID: post.postID,
            post_time: post.post_time,
            user: post.user,
            text: post.text,
            url: post.url,
            images: post.images.map((image: PixPostImage, index: number) => {
                return {
                    id: `${post.postID}_${index}`,
                    url: image,
                    selected: true,
                }
            }),
        }
    })
    isLoadImages.value = false
    dlName.value = search.value.tag !== '' ? search.value.tag : ''
}

// 画像情報から画像URLのみを抜き出す
const getSelectedImagesFromPosts = (pixPosts: PixPostInfo[]) => {
    const images: string[] = []
    pixPosts.map((post) => {
        post.images.map((image) => {
            if (image.selected) images.push(image.url)
        })
    })

    return images
}

// 画像のダウンロード
const dlImage = async () => {
    isLoadImages.value = true
    // 画像URL一覧の作成
    const imagePaths = getSelectedImagesFromPosts(pixPostInfo.value)

    // 画像URL一覧をAPIに送り画像をDL
    const downloadResponse = await apiManager.post(
        `${apiPath}/pixiv/downloadImages`,
        {
            content: imagePaths,
            dlName: dlName.value,
        }
    )

    // 画像のDLとzipファイルの作成に成功した場合、zipをDLする
    if (downloadResponse.error) {
        errorMessage.value = downloadResponse.content
        return
    }

    const link = document.createElement('a')
    link.href = `${apiPath}/pixiv/getZip`
    document.body.appendChild(link)
    link.click()
    link.setAttribute('download', ``)
    document.body.removeChild(link)

    const posts = {
        imageCount: imagePaths.length,
        latestID:
            search.value.getPostType === 'tag'
                ? pixPostInfo.value[pixPostInfo.value.length - 1].postID
                : pixPostInfo.value[0].postID,
        getPostType: search.value.getPostType,
        tag: search.value.tag,
        pixUserID: search.value.userID,
    }

    // DL完了時、DL回数・枚数と最新DL画像の投稿IDを更新
    await apiManager.post(`${apiPath}/api/updatePixivInfo`, posts)
    isLoadImages.value = false
}

onMounted(async () => {
    const userInfo = await getUserInfo()
    search.value.userID = userInfo[0]['id']
    search.value.suspendID = userInfo[0]['post']
})
</script>
<template>
    <HeaderComponent />
    <main class="main-container twi-template">
        <section class="common-form">
            <dl class="form-box">
                <div>
                    <dt>
                        取得内容
                        <em>*</em>
                    </dt>
                    <dd class="radio-list">
                        <div>
                            <input
                                id="get-bookmark"
                                v-model="search.getPostType"
                                type="radio"
                                value="bookmark"
                            />
                            <label for="get-bookmark">ブックマーク</label>
                        </div>
                        <div>
                            <input
                                id="get-post"
                                v-model="search.getPostType"
                                type="radio"
                                value="post"
                            />
                            <label for="get-post">作品</label>
                        </div>
                        <div>
                            <input
                                id="get-keyword"
                                v-model="search.getPostType"
                                type="radio"
                                value="tag"
                            />
                            <label for="get-keyword">タグ</label>
                        </div>
                    </dd>
                </div>
                <div v-if="search.getPostType === 'tag'">
                    <dt>タグキーワード</dt>
                    <dd>
                        <input type="text" id="tag" v-model="search.tag" />
                    </dd>
                </div>
                <div v-if="search.getPostType === 'tag'">
                    <dt>ブックマーク数下限</dt>
                    <dd>
                        <input
                            type="number"
                            id="min-bookmark"
                            v-model="search.minBookmarks"
                        />
                    </dd>
                </div>
                <div v-else>
                    <dt>ユーザーID</dt>
                    <dd>
                        <input
                            type="number"
                            id="user-id"
                            v-model="search.userID"
                        />
                    </dd>
                </div>
                <div>
                    <dt>取得投稿数</dt>
                    <dd>
                        <input
                            type="number"
                            id="get-post-num"
                            v-model="search.getNumberOfPost"
                        />
                    </dd>
                </div>
                <div>
                    <dt>取得を中断するID</dt>
                    <dd>
                        <input
                            type="number"
                            id="suspend-id"
                            v-model="search.suspendID"
                        />
                    </dd>
                </div>
                <div>
                    <dt>詳細設定</dt>
                    <dd>
                        <input
                            id="get-pre"
                            v-model="search.isGetFromPreviousPost"
                            type="checkbox"
                        />
                        <label for="get-pre">取得を中断するIDを設定</label>
                        <input
                            id="include-tags"
                            v-model="search.includeTags"
                            type="checkbox"
                        />
                        <label for="include-tags">タグフィルターを設定</label>
                        <input
                            id="ignore-sensitive"
                            v-model="search.isIgnoreSensitive"
                            type="checkbox"
                        />
                        <label for="ignore-sensitive">R-18作品を除外する</label>
                    </dd>
                </div>
                <div v-show="isLoadImages" class="btn-cover"></div>
                <ButtonComponent
                    @click="getImage()"
                    text="作品を取得"
                    :buttonClass="'btn-common green'"
                />
            </dl>
        </section>
        <p>{{ errorMessage }}</p>
        <section v-if="pixPostInfo.length > 0" class="post-list">
            <div v-show="isLoadImages" class="btn-cover"></div>
            <div class="title-area">
                <h2>取得投稿一覧</h2>
                <p v-if="pixPostInfo.length > 0" class="caption">
                    取得投稿数: {{ pixPostInfo.length }}
                </p>
            </div>
            <div class="dl-image-area">
                <label for="dl-name">保存名</label>
                <input type="text" id="dl-name" v-model="dlName" />
                <ButtonComponent
                    @click="dlImage()"
                    text="ダウンロード"
                    :buttonClass="'btn-common green'"
                />
                <p class="caption">※選択している画像をDLします。</p>
            </div>
            <div
                v-for="pixPost in pixPostInfo"
                :key="pixPost.postID"
                class="post-info"
            >
                <h3 class="user-name">{{ pixPost.user }}</h3>
                <p class="pix-post-text">{{ pixPost.text }}</p>
                <div class="pix-post-image">
                    <div
                        v-for="(image, index) in pixPost.images"
                        :key="image.id"
                    >
                        <input
                            :id="image.id"
                            v-model="image.selected"
                            type="checkbox"
                        />
                        <label
                            :for="image.id"
                            :class="!image.selected ? 'not-selected' : ''"
                        >
                            {{ `${index + 1}枚目: ${image.id}` }}
                        </label>
                    </div>
                </div>
                <div class="post-url">
                    <p>作品元リンク</p>
                    <a :href="pixPost.url">{{ pixPost.url }}</a>
                </div>
            </div>
        </section>
    </main>
</template>
