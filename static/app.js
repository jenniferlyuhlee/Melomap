const BASE_URL = "http://localhost:5000/";


// axios request to view bookmarked songs without reload
async function displayBookmarkedSongs(evt){
    let $target = $(evt.target)
    const userId = $target.data("userid")
    // send request
    const htmlResp = await axios.get(`${BASE_URL}users/${userId}/bookmarked`)
    const htmlRespString = htmlResp.data
    // change display to reflect response data
    $('#user-content').empty().append(htmlRespString)
    // change active-tab 
    $target.parent().prev().removeClass('active-tab')
    $target.parent().addClass('active-tab')
}
$('#my-songs-tab').on('click', displayBookmarkedSongs)


//axios request to view posts without reload
async function displayPosts(evt){
    let $target = $(evt.target)
    const userId = $target.data("userid")
    // send request
    const htmlResp = await axios.get(`${BASE_URL}users/${userId}/posts`)
    const htmlRespString = htmlResp.data
    // change display to reflect response data
    $('#user-content').empty().append(htmlRespString)
    // change active-tab 
    $target.parent().next().removeClass('active-tab')
    $target.parent().addClass('active-tab')
}
$('#my-posts-tab').on('click', displayPosts)


// axios request to bookmark/unbookmark songs
async function toggleBookmark(evt){
    let $target = $(evt.target)
    const songId = $target.parent().parent().attr('id')
    const resp = await axios.post(`${BASE_URL}bookmark/${songId}`)
    if (resp){
        if ($target.hasClass('bi-bookmark')){
            $target.removeClass('bi-bookmark')
            $target.addClass('bi-bookmark-fill')
        }
        else{
            $target.removeClass('bi-bookmark-fill')
            $target.addClass('bi-bookmark')
        }
    }
}
$('.bookmark').on('click', toggleBookmark)


// axios request to delete a post
async function deletePost(evt){
    let $target = $(evt.target)
    const postId = $target.parent().parent().attr('id')
    const resp = await axios.delete(`${BASE_URL}posts/${postId}/delete`)

    if (resp.data.message === "Deleted"){
        let $postEl = $target.closest(`#${postId}`)
        $postEl.remove()
        alert('Success: Post deleted.')
    }
    else{
        alert('Server Error: Failed to delete.')
    }
}
$('.fa-trash-can').on('click', deletePost)


// Handle radio form for search filtering
function filter_results(){
    const val = $('input[name="filter"]:checked').val();
    if (val === 'users'){
        $('#music-results').hide()
        $('#users-results').show()
    }
    else{
        $('#music-results').show()
        $('#users-results').hide()
    }
}
$('.filter').change(filter_results)


// Click event to play/pause track audio snippet
$('.play-pause').on('click', playPause)
function playPause(evt){
    let $iconBtn = $(evt.target)
    let audioId = $iconBtn.parent().prev().attr('id')
    let $audio = $(`#${audioId}`).get(0)
    if ($iconBtn.hasClass('bi-play-fill')){
        $iconBtn.removeClass('bi-play-fill')
        $iconBtn.addClass('bi-pause-fill')
        $audio.play();
    }
    else{
        $iconBtn.removeClass('bi-pause-fill')
        $iconBtn.addClass('bi-play-fill')
        $audio.pause()
    }
}