from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from apps.catalog.models import Product, ProductImage, ProductVideo
from apps.core.utils import is_staff_member


@user_passes_test(is_staff_member, login_url='/auth/login/')
@require_POST
def product_image_upload(request):
    """AJAX upload of product gallery images."""
    product_id = request.POST.get('product_id')
    session_token = request.POST.get('session_token', '')
    image_file = request.FILES.get('image')

    if not image_file:
        return JsonResponse({'success': False, 'error': 'No image file uploaded.'}, status=400)

    # Determine order (next index)
    if product_id:
        product = get_object_or_404(Product, pk=product_id)
        current_count = ProductImage.objects.filter(product=product).count()
        # First image uploaded becomes cover if product has no cover
        is_cover = not ProductImage.objects.filter(product=product, is_cover=True).exists() and not product.cover_image
        img = ProductImage.objects.create(
            product=product,
            image=image_file,
            order=current_count,
            is_cover=is_cover
        )
        if is_cover:
            product.cover_image = img.image
            product.save(update_fields=['cover_image'])
    else:
        if not session_token:
            return JsonResponse({'success': False, 'error': 'No session token provided.'}, status=400)
        current_count = ProductImage.objects.filter(session_token=session_token).count()
        is_cover = not ProductImage.objects.filter(session_token=session_token, is_cover=True).exists()
        img = ProductImage.objects.create(
            session_token=session_token,
            image=image_file,
            order=current_count,
            is_cover=is_cover
        )

    return JsonResponse({
        'success': True,
        'id': img.id,
        'url': img.image.url,
        'is_cover': img.is_cover
    })


@user_passes_test(is_staff_member, login_url='/auth/login/')
@require_POST
def product_image_delete(request):
    """AJAX delete of a gallery image."""
    image_id = request.POST.get('image_id')
    img = get_object_or_404(ProductImage, pk=image_id)
    product = img.product
    was_cover = img.is_cover

    img.image.delete(save=False)
    img.delete()

    # If the deleted image was the cover, assign a new cover
    if was_cover:
        if product:
            next_img = ProductImage.objects.filter(product=product).order_by('order').first()
            if next_img:
                next_img.is_cover = True
                next_img.save(update_fields=['is_cover'])
                product.cover_image = next_img.image
                product.save(update_fields=['cover_image'])
            else:
                product.cover_image = None
                product.save(update_fields=['cover_image'])
        else:
            session_token = request.POST.get('session_token')
            if session_token:
                next_img = ProductImage.objects.filter(session_token=session_token).order_by('order').first()
                if next_img:
                    next_img.is_cover = True
                    next_img.save(update_fields=['is_cover'])

    return JsonResponse({'success': True})


@user_passes_test(is_staff_member, login_url='/auth/login/')
@require_POST
def product_image_reorder(request):
    """AJAX reorder of gallery images."""
    image_ids = request.POST.getlist('image_ids[]')
    for index, image_id in enumerate(image_ids):
        ProductImage.objects.filter(pk=image_id).update(order=index)
    return JsonResponse({'success': True})


@user_passes_test(is_staff_member, login_url='/auth/login/')
@require_POST
def product_image_set_cover(request):
    """AJAX set cover/primary image."""
    image_id = request.POST.get('image_id')
    img = get_object_or_404(ProductImage, pk=image_id)
    product = img.product

    if product:
        ProductImage.objects.filter(product=product).update(is_cover=False)
        img.is_cover = True
        img.save(update_fields=['is_cover'])
        product.cover_image = img.image
        product.save(update_fields=['cover_image'])
    else:
        session_token = img.session_token
        if session_token:
            ProductImage.objects.filter(session_token=session_token).update(is_cover=False)
            img.is_cover = True
            img.save(update_fields=['is_cover'])

    return JsonResponse({'success': True})


@user_passes_test(is_staff_member, login_url='/auth/login/')
@require_POST
def product_video_upload(request):
    """AJAX upload of product videos."""
    product_id = request.POST.get('product_id')
    session_token = request.POST.get('session_token', '')
    video_file = request.FILES.get('video')

    if not video_file:
        return JsonResponse({'success': False, 'error': 'No video file uploaded.'}, status=400)

    if product_id:
        product = get_object_or_404(Product, pk=product_id)
        current_count = ProductVideo.objects.filter(product=product).count()
        video_obj = ProductVideo.objects.create(
            product=product,
            video=video_file,
            order=current_count
        )
    else:
        if not session_token:
            return JsonResponse({'success': False, 'error': 'No session token provided.'}, status=400)
        current_count = ProductVideo.objects.filter(session_token=session_token).count()
        video_obj = ProductVideo.objects.create(
            session_token=session_token,
            video=video_file,
            order=current_count
        )

    return JsonResponse({
        'success': True,
        'id': video_obj.id,
        'url': video_obj.video.url
    })


@user_passes_test(is_staff_member, login_url='/auth/login/')
@require_POST
def product_video_delete(request):
    """AJAX delete of a product video."""
    video_id = request.POST.get('video_id')
    video_obj = get_object_or_404(ProductVideo, pk=video_id)
    video_obj.video.delete(save=False)
    video_obj.delete()
    return JsonResponse({'success': True})


@user_passes_test(is_staff_member, login_url='/auth/login/')
@require_POST
def product_video_reorder(request):
    """AJAX reorder of product videos."""
    video_ids = request.POST.getlist('video_ids[]')
    for index, video_id in enumerate(video_ids):
        ProductVideo.objects.filter(pk=video_id).update(order=index)
    return JsonResponse({'success': True})
